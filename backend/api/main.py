from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.gemini_parser import GeminiParser
from calculator.tax_calculator import FIFOTaxCalculator
from database.models import TaxReport, Transaction, get_db
from api.schemas import (
    TaxSummaryResponse,
    TaxReportListItem,
    UploadResponse,
    ErrorResponse,
    CapitalGainSchema
)
from integrations.gemini_client import GeminiAPIClient
from database.models import APIKey
from api.schemas import APIKeyInput, GeminiSyncRequest, GeminiSyncResponse

# Initialize FastAPI app
app = FastAPI(
    title="Crypto Tax Calculator API",
    description="Calculate capital gains/losses for cryptocurrency trading",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "Crypto Tax Calculator API",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/upload", response_model=UploadResponse)
async def upload_csv(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    """
    Upload a Gemini CSV file and calculate taxes

    Returns:
        UploadResponse with report_id and summary
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Parse CSV
        parser = GeminiParser(temp_path)
        transactions = parser.parse()

        if not transactions:
            raise HTTPException(status_code=400, detail="No transactions found in CSV")

        # Calculate taxes
        calculator = FIFOTaxCalculator()
        tax_summary = calculator.calculate_taxes(transactions)

        # Convert capital gains to dict format for JSON storage
        capital_gains_data = []
        for gain in tax_summary['capital_gains']:
            capital_gains_data.append({
                'sale_date': gain.sale_date.isoformat(),
                'purchase_date': gain.purchase_date.isoformat(),
                'symbol': gain.symbol,
                'amount': gain.amount,
                'cost_basis': gain.cost_basis,
                'proceeds': gain.proceeds,
                'gain_loss': gain.gain_loss,
                'term': gain.term,
                'holding_days': gain.holding_days
            })

        # Save to database
        tax_report = TaxReport(
            filename=file.filename,
            total_gain_loss=tax_summary['total_gain_loss'],
            short_term_gain_loss=tax_summary['short_term_gain_loss'],
            long_term_gain_loss=tax_summary['long_term_gain_loss'],
            num_transactions=tax_summary['num_transactions'],
            num_short_term=tax_summary['num_short_term'],
            num_long_term=tax_summary['num_long_term'],
            detailed_report={
                'capital_gains': capital_gains_data,
                'errors': tax_summary['errors']
            }
        )

        db.add(tax_report)
        db.commit()
        db.refresh(tax_report)

        # Save transactions
        for txn in transactions:
            transaction = Transaction(
                report_id=tax_report.id,
                date=txn['date'],
                type=txn['type'],
                symbol=txn['symbol'],
                amount=txn['amount'],
                price_per_unit=txn['price_per_unit'],
                price_usd=txn['price_usd'],
                fee_usd=txn['fee_usd']
            )
            db.add(transaction)

        db.commit()

        # Clean up temp file
        os.remove(temp_path)

        return UploadResponse(
            message="Tax calculation completed successfully",
            report_id=tax_report.id,
            filename=file.filename,
            num_transactions=len(transactions)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/reports", response_model=List[TaxReportListItem])
def get_all_reports(db: Session = Depends(get_db)):
    """
    Get list of all tax reports

    Returns:
        List of tax report summaries
    """
    reports = db.query(TaxReport).order_by(TaxReport.upload_date.desc()).all()
    return reports


@app.get("/reports/{report_id}", response_model=TaxSummaryResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """
    Get detailed tax report by ID

    Args:
        report_id: The ID of the tax report

    Returns:
        Detailed tax summary with all capital gains
    """
    report = db.query(TaxReport).filter(TaxReport.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Convert stored JSON back to CapitalGainSchema objects
    capital_gains = []
    for gain_data in report.detailed_report.get('capital_gains', []):
        capital_gains.append(CapitalGainSchema(
            sale_date=datetime.fromisoformat(gain_data['sale_date']),
            purchase_date=datetime.fromisoformat(gain_data['purchase_date']),
            symbol=gain_data['symbol'],
            amount=gain_data['amount'],
            cost_basis=gain_data['cost_basis'],
            proceeds=gain_data['proceeds'],
            gain_loss=gain_data['gain_loss'],
            term=gain_data['term'],
            holding_days=gain_data['holding_days']
        ))

    return TaxSummaryResponse(
        report_id=report.id,
        filename=report.filename,
        total_gain_loss=report.total_gain_loss,
        short_term_gain_loss=report.short_term_gain_loss,
        long_term_gain_loss=report.long_term_gain_loss,
        num_transactions=report.num_transactions,
        num_short_term=report.num_short_term,
        num_long_term=report.num_long_term,
        capital_gains=capital_gains,
        upload_date=report.upload_date
    )


@app.delete("/reports/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    """
    Delete a tax report

    Args:
        report_id: The ID of the tax report to delete
    """
    report = db.query(TaxReport).filter(TaxReport.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Delete associated transactions
    db.query(Transaction).filter(Transaction.report_id == report_id).delete()

    # Delete report
    db.delete(report)
    db.commit()

    return {"message": "Report deleted successfully", "report_id": report_id}


@app.get("/health")
def health_check():
    """Health check for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api-keys/test")
async def test_api_key(api_key_data: APIKeyInput):
    """Test if Gemini API credentials are valid

    Returns:
        Success/failure message
    """

    try:
        client = GeminiAPIClient(
            api_key_data.api_key,
            api_key_data.api_secret,
            sandbox=api_key_data.is_sandbox
        )

        if client.test_conection():
            return {"message": "API credentials are valid", "status": "success"}
        else:
            raise HTTPException(status_code=400, detail="Invalid API credentials")
    except Exception as e:
        return HTTPException(status_code=400, detail=f"Error testing credentials: {str(e)}")

@app.post("/gemini/sync", response_model=GeminiSyncResponse)
async def sync_from_gemini(
        api_key_data: APIKeyInput,
        sync_request: GeminiSyncRequest,
        db: Session = Depends(get_db)
):
    """
    Fetch transactions directly from Gemini API and calculate taxes

    Args:
        api_key_data: The API key data
        sync_request: Sync parameters (symbol, limit)
    Returns:
        GeminiSyncResponse with report_id
    """

    try:
        #Initlize Gemini client
        client = GeminiAPIClient(
            api_key_data.api_key,
            api_key_data.api_secret,
            sandbox=api_key_data.is_sandbox
        )

        #Fetch trades from Gemini
        trades = client.get_past_trades(
            symbol=sync_request.symbol,
            limit=sync_request.limit
        )

        if not trades:
            raise HTTPException(status_code=400, detail="No trades found in Gemini account")

        #Convert to parser format
        symbol = sync_request.symbol[:3].upper() # 'btcusd' -> 'BTC'
        transactions = client.convert_to_parser_format(trades, symbol=symbol)

        #Calculate taxes using exisitng calculator
        calculator = FIFOTaxCalculator()
        tax_summary = calculator.calculate_taxes(transactions)

        #Convert capital gains to dict format for JSON storage
        capital_gains_data = []
        for gain in tax_summary['capital_gains']:
            capital_gains_data.append({
                'sale_date': gain.sale_date.isoformat(),
                'purchase_date': gain.purchase_date.isoformat(),
                'symbol': gain.symbol,
                'amount': gain.amount,
                'cost_basis': gain.cost_basis,
                'proceeds': gain.proceeds,
                'gain_loss': gain.gain_loss,
                'term': gain.term,
                'holding_days': gain.holding_days
            })

            #Save to database
            filename = f"gemini_api_sync_{sync_request.symbol}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

            tax_report = TaxReport(
                filename=filename,
                total_gain_loss=tax_summary['total_gain_loss']
                short_term_gain_loss=tax_summary['short_term_gain_loss'],
                long_term_gain_loss=tax_summary['long_term_gain_loss'],
                num_transactions=tax_summary['num_transactions'],
                num_short_term=tax_summary['num_short_term'],
                num_long_term=tax_summary['num_long_term'],
                detailed_report={
                    'capital_gains': capital_gains_data,
                    'errors': tax_summary['errors'],
                    'source': 'gemini_api',
                    'symbol': sync_request.symbol
                }
            )

            db.add(tax_report)
            db.commit()
            db.refresh(tax_report)

            #Save transactions
            for txn in transactions:
                transaction = Transaction(
                    report_id = tax_report.id,
                    date=txn['date'],
                    type=txn['type'],
                    symbol=txn['symbol'],
                    amount=txn['amount'],
                    price_per_unit=txn['price_per_unit'],
                    price_usd=txn['price_usd'],
                    fee_usd=txn['fee_usd'],
                )
                db.add(transaction)
            db.commit()

            return GeminiSyncResponse(
                mmessage="Successfully fetched transactions from Gemini API",
                report_id=tax_report.report_id,
                num_transactions=len(transactions),
                exchange = "gemini"
            )
    except Exception as e:
        raise HTTPException(status_code = 500, detail=f"Error syncing from Gemini: {str(e)}")

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class TransactionSchema(BaseModel):
    """Schema for a single transaction"""
    date: datetime
    type: str
    symbol: str
    amount: float
    price_per_unit: float
    price_usd: float
    fee_usd: float

    class Config:
        from_attributes = True

class CapitalGainSchema(BaseModel):
    """Schema for a single capital gain"""
    sale_date: datetime
    purchase_date: datetime
    symbol: str
    amount: float
    cost_basis: float
    proceeds: float
    gain_loss: float
    term: str
    holding_days: int

class TaxSummaryResponse(BaseModel):
    """Schema for a single tax summary reps"""
    report_id: int
    filename: str
    total_gain_loss: float
    short_term_gain_loss: float
    long_term_gain_loss: float
    num_transactions: int
    num_short_term: int
    num_long_term: int
    capital_gains: List[CapitalGainSchema]
    upload_date: datetime

    class Config:
        from_attributes = True

class TaxReportListItem(BaseModel):
    """Schema for a single tax report list"""
    id: int
    filename: str
    upload_date: datetime
    total_gain_loss: float
    num_transactions: int

    class Config:
        from_attributes = True

class UploadResponse(BaseModel):
    """Response after file upload"""
    message: str
    report_id: int
    filename: str
    num_transactions: int

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None

class APIKeyInput(BaseModel):
    """Input schema for API keY"""
    api_key: str
    api_secret: str
    is_sandbox: bool = False

class GeminiSyncRequest(BaseModel):
    """Request to sync transaction from Gemini"""
    symbol: str = "btcusd"
    limit: int = 500

class GeminiSyncResponse(BaseModel):
    """Response after syncing from Gemini"""
    message: str
    report_id: int
    num_transactions: int
    exchange: str = "gemini"
# Crypto Tax Calculator

A full-stack web application that automates cryptocurrency capital gains and losses calculations using FIFO (First-In-First-Out) methodology. Built for traders who need accurate tax reporting data for IRS Form 8949.

## Overview

This application solves the problem of calculating cost basis for cryptocurrency trades. When you buy and sell crypto, the IRS requires you to report capital gains using specific accounting methods. Manually calculating this for hundreds of transactions is time-consuming and error-prone. This app automates the entire process.

## Features

- **FIFO Tax Calculations**: Automatically matches sales to oldest purchases
- **Capital Gains Classification**: Separates short-term (≤365 days) and long-term (>365 days) gains
- **Dual Input Methods**: Upload CSV files or connect directly via Gemini API
- **Detailed Reports**: Line-by-line breakdown of each capital gain/loss
- **Persistent Storage**: Save and retrieve historical tax calculations
- **Modern UI**: Clean, responsive interface built with React

## Tech Stack

### Backend
- **Python 3.9+**: Core language
- **FastAPI**: Web framework with automatic API documentation
- **SQLAlchemy**: ORM for database operations
- **Pandas**: CSV parsing and data manipulation
- **SQLite**: Database (easily upgradeable to PostgreSQL)

### Frontend
- **React 19**: UI library
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **Axios**: HTTP client

## Installation

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm

### Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/crypto-tax-calculator.git
cd crypto-tax-calculator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`

API documentation available at `http://localhost:8000/docs`

### Frontend Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at `http://localhost:3000`

## Usage

### Method 1: CSV Upload

1. Download transaction history from Gemini (Account → Transaction History → Export CSV)
2. Open the app and navigate to "Calculate Taxes"
3. Upload your CSV file
4. View your tax report with detailed breakdown

### Method 2: API Integration

1. Create API credentials in Gemini (Settings → API → Create New Key)
2. In the app, click "Connect Gemini API"
3. Enter API Key and Secret
4. Select trading pair and click "Sync Transactions"
5. View automatically generated tax report

## How It Works

### FIFO Algorithm

The app implements First-In-First-Out matching:

1. Each purchase creates a "tax lot" with date and cost basis
2. When you sell, the app matches against the oldest lot first
3. Sales may span multiple lots if the amount exceeds a single lot
4. Holding period determines short-term vs. long-term classification

### Example Calculation

```
Jan 15: BUY  1.0 BTC at $40,000
Feb 20: BUY  0.5 BTC at $50,000
Mar 10: SELL 1.2 BTC at $60,000

FIFO Matching:
  1.0 BTC from Jan 15 purchase:
    Cost basis: $40,000
    Proceeds: $60,000
    Gain: $20,000 (short-term, 54 days)
  
  0.2 BTC from Feb 20 purchase:
    Cost basis: $10,000
    Proceeds: $12,000
    Gain: $2,000 (short-term, 18 days)

Total: $22,000 short-term capital gain
```

## API Endpoints

### POST /upload
Upload CSV file for tax calculation

**Response:**
```json
{
  "report_id": 1,
  "filename": "transactions.csv",
  "num_transactions": 25
}
```

### GET /reports
List all saved tax reports

### GET /reports/{id}
Get detailed report with all capital gains

### DELETE /reports/{id}
Delete a tax report

### POST /gemini/sync
Fetch transactions directly from Gemini API

**Request:**
```json
{
  "api_key": "account-xxx",
  "api_secret": "xxx",
  "symbol": "btcusd",
  "limit": 500
}
```

## Project Structure

```
crypto-tax-calculator/
├── main.py                 # FastAPI routes and application
├── tax_calculator.py       # FIFO algorithm implementation
├── gemini_parser.py        # CSV parsing
├── gemini_client.py        # Gemini API integration
├── models.py               # Database models (SQLAlchemy)
├── schemas.py              # Request/response validation (Pydantic)
├── requirements.txt        # Python dependencies
├── App.jsx                 # Main React component
├── components/
│   ├── FileUpload.jsx
│   ├── GeminiAPIForm.jsx
│   ├── TaxSummary.jsx
│   ├── TransactionTable.jsx
│   └── ReportsList.jsx
└── services/
    └── api.js              # API client functions
```

## Architecture

### System Design

The application uses a layered architecture with clear separation of concerns:

**API Layer** (`main.py`): Handles HTTP requests, validation, and response formatting

**Business Logic Layer**:
- `tax_calculator.py`: FIFO algorithm and capital gains calculation
- `gemini_parser.py`: CSV to transaction conversion
- `gemini_client.py`: Gemini API integration and format conversion

**Data Layer** (`models.py`): Database operations via SQLAlchemy ORM

**Presentation Layer** (React): User interface and client-side state management

### Design Patterns

- **Adapter Pattern**: Both CSV and API inputs convert to standardized internal format
- **Dependency Injection**: Database sessions injected via FastAPI's `Depends()`
- **Repository Pattern**: Database access abstracted through ORM
- **MVC**: Clear separation between routes, business logic, and data models

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest test_tax_calculator.py
```

Test coverage includes:
- FIFO algorithm correctness
- Partial lot sales
- Short-term vs. long-term classification
- Multiple lots in single sale
- Edge cases and error handling

## Future Enhancements

### Tax Features
- Support for LIFO and HIFO cost basis methods
- Wash sale detection and adjustment
- Staking rewards and airdrops handling
- Multi-currency support (ETH, SOL, etc.)

### Technical Improvements
- User authentication and multi-user support
- PostgreSQL migration for production
- API rate limiting and caching
- Background job processing for large datasets
- Export to IRS Form 8949 PDF

### Integrations
- Support for additional exchanges (Coinbase, Kraken, Binance)
- TurboTax/TaxAct direct import
- Portfolio tracking and performance metrics

## Important Notes

**This application calculates capital gains and losses, not actual tax owed.** Tax liability depends on your total income, tax bracket, filing status, and other factors. The app provides the data needed for IRS Form 8949. Consult a tax professional for official tax advice.

**Security:** API secrets are currently stored in plaintext. For production use, implement encryption at rest using libraries like `cryptography.fernet` and store encryption keys in environment variables or a secrets manager.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For questions or feedback, please open an issue on GitHub.
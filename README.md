# Crypto Tax Calculator

A web application that helps crypto traders calculate capital gains/losses for tax reporting.

## Project Status
🚧 **In Development** - Currently building MVP

### Completed
- ✅ Project structure setup
- ✅ CSV parser for Gemini transactions

### In Progress
- 🔄 FIFO tax calculation engine

### Upcoming
- ⏳ FastAPI backend
- ⏳ React frontend
- ⏳ PDF report generation

## Tech Stack
- **Backend**: Python, FastAPI, Pandas
- **Frontend**: React, TypeScript
- **Database**: PostgreSQL
- **Deployment**: Railway/Vercel

## Getting Started

### Prerequisites
- Python 3.9+
- pip

### Installation
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Parser
```bash
cd backend/parsers
python gemini_parser.py
```

## Project Structure
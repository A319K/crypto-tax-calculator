#SQLite for now, but switch to PostgreSQL later
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, create_engine, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class TaxReport(Base):
    """Stores calculated tax reports in the database"""
    __tablename__ = "tax_report"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    total_gain_loss = Column(Float)
    short_term_gain_loss = Column(Float)
    long_term_gain_loss = Column(Float)
    num_transactions = Column(Integer)
    num_short_term = Column(Integer)
    num_long_term = Column(Integer)

    #Store the full report as a JSON
    detailed_report = Column(JSON)

    def __repr__(self):
        return f"<TaxReport(id={self.id}, file={self.filename}, gain=${self.total_gain_loss})>"

class Transaction(Base):
    """Stores individual transactions in the database"""

    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, index=True) #Links to TaxReport
    date = Column(DateTime)
    type = Column(String) #Buy or sell
    symbol = Column(String)
    amount = Column(Float)
    price_per_unit = Column(Float)
    price_usd = Column(Float)
    fee_usd = Column(Float)

    def __erpr__(self):
        return f"<Transaction({self.type} {self.amount} {self.symbol})>"

class APIKey(Base):
    """Stores API keys in the database"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key= True, index = True)
    user_id = Column(String, index = True) #For future user auth
    exchange = Column(String, default = "gemini")
    api_key = Column(String, nullable = False)
    api_secret = Column(String, nullable = False) #Should be encrypted in production
    is_sandbox = Column(Boolean, default = False)
    created_at = Column(DateTime, default = datetime.utcnow)
    last_used = Column(DateTime)

    def __repr__(self):
        return f"<APIKey(exchange={self.exchange}, sandbox={self.is_sandbox})>"



#Database setup
DATABASE_URL = "sqlite:///./tax_calculator.db"
# Using SQLite for easy setup
# For PostgreSQL later: "postgresql://user:password@localhost/dbname"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

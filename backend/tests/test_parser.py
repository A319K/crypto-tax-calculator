import pytest
import sys
import os
from datetime import datetime


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.gemini_parser import GeminiParser

class TestGeminiParser:
    """Test suite for Gemini CSV Parser"""

    def test_parser_loads_csv(self):
        #Test that parser can load the sample CSV file
        parser = GeminiParser('../sample_data/gemini_sample.csv')
        transactions = parser.parse()
        assert len(transactions) == 4 #Should parse 4 transactions

    def test_transaction_structure(self):
        #Test that parsed transaction have correct structure
        parser = GeminiParser('../sample_data/gemini_sample.csv')
        transactions = parser.parse()

        #Check if first transaction has all required fields
        first_tx = transactions[0]
        required_fields = ['date', 'type', 'symbol', 'amount', 'price_usd', 'fee_usd', 'price_per_unit']

        for field in required_fields:
            assert field in first_tx, f"Transaction missing field: {field}"

    def test_buy_transactions(self):
        #Test that BUY trasactions are parsed correctly
        parser = GeminiParser('../sample_data/gemini_sample.csv')
        transactions = parser.parse()

        buys = [t for t in transactions if t['type'] == 'buy']

        assert len(buys) == 2, "Should have 2 buy transactions"
        assert buys[0]['amount'] == 0.11, "First buy should be 0.11 BTC"
        assert buys[0]['price_usd'] == 5000.00, "First buy should cost $5000"

    def test_sell_transactions(self):
        #Test that SELL transactions are parsed correctly
        parser = GeminiParser('../sample_data/gemini_sample.csv')
        transactions = parser.parse()

        sells = [t for t in transactions if t['type'] == 'sell']

        assert len(sells) == 2, "Should have 2 sell transactions"
        assert sells[0]['amount'] == 0.10, "First sell should be 0.10 BTC"
        assert sells[0]['price_usd'] == 7000.00, "First sell should receive $7000"

    def test_date_parsing(self):
        #Test that dates are parsed correctly
        parser = GeminiParser('../sample_data/gemini_sample.csv')
        transactions = parser.parse()

        first_date = transactions[0]['date']

        assert isinstance(first_date, datetime), "First date should be a datetime object"
        assert first_date.year == 2024, "Year should be 2024"
        assert first_date.month == 1, "Month should be January"
        assert first_date.day == 15, "Day should be 15"

    def test_price_per_unit_calculation(self):
        #Test that price per unit is calculated correctly
        parser = GeminiParser('../sample_data/gemini_sample.csv')
        transactions = parser.parse()

        first_tx = transactions[0]
        expected_price = first_tx['price_usd'] / first_tx['amount']

        assert abs(first_tx['price_per_unit'] - expected_price) < 0.01, \
            "Price per unit calculation should be accurate"

    def test_summary_statistics(self):
        #Test that summary statistics are correct
        parser = GeminiParser('../sample_data/gemini_sample.csv')
        parser.parse()
        summary = parser.get_summary()

        assert summary['total_transactions'] == 4
        assert summary['total_buys'] == 2
        assert summary['total_sells'] == 2
        assert summary['total_spent'] == 8000.00
        assert summary['total_received'] == 12000.00


# Run tests when this file is executed
if __name__ == "__main__":
    pytest.main([__file__, '-v'])




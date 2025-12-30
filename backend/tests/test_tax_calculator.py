import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calculator.tax_calculator import FIFOTaxCalculator, TaxLot, CapitalGain


class TestFIFOTaxCalculator:
    """Test suite for FIFO tax calculator"""

    def test_simple_buy(self):
        """Test that buying creates a tax lot"""
        calculator = FIFOTaxCalculator()

        buy_transaction = {
            'date': datetime(2024, 1, 1),
            'type': 'buy',
            'symbol': 'BTC',
            'amount': 1.0,
            'price_per_unit': 50000.0,
            'price_usd': 50000.0,
            'fee_usd': 10.0
        }

        calculator.process_transaction(buy_transaction)

        assert len(calculator.lots) == 1
        assert calculator.lots[0].amount == 1.0
        assert calculator.lots[0].price_per_unit == 50000.0

    def test_simple_gain(self):
        """Test a simple profitable sale"""
        calculator = FIFOTaxCalculator()

        transactions = [
            {
                'date': datetime(2024, 1, 1),
                'type': 'buy',
                'symbol': 'BTC',
                'amount': 1.0,
                'price_per_unit': 50000.0,
                'price_usd': 50000.0,
                'fee_usd': 10.0
            },
            {
                'date': datetime(2024, 2, 1),
                'type': 'sell',
                'symbol': 'BTC',
                'amount': 1.0,
                'price_per_unit': 60000.0,
                'price_usd': 60000.0,
                'fee_usd': 15.0
            }
        ]

        summary = calculator.calculate_taxes(transactions)

        assert summary['total_gain_loss'] == 10000.0
        assert summary['num_transactions'] == 1
        assert len(calculator.lots) == 0  # All sold

    def test_simple_loss(self):
        """Test a losing sale"""
        calculator = FIFOTaxCalculator()

        transactions = [
            {
                'date': datetime(2024, 1, 1),
                'type': 'buy',
                'symbol': 'BTC',
                'amount': 1.0,
                'price_per_unit': 60000.0,
                'price_usd': 60000.0,
                'fee_usd': 10.0
            },
            {
                'date': datetime(2024, 2, 1),
                'type': 'sell',
                'symbol': 'BTC',
                'amount': 1.0,
                'price_per_unit': 50000.0,
                'price_usd': 50000.0,
                'fee_usd': 15.0
            }
        ]

        summary = calculator.calculate_taxes(transactions)

        assert summary['total_gain_loss'] == -10000.0

    def test_partial_sale(self):
        """Test selling part of a lot"""
        calculator = FIFOTaxCalculator()

        transactions = [
            {
                'date': datetime(2024, 1, 1),
                'type': 'buy',
                'symbol': 'BTC',
                'amount': 1.0,
                'price_per_unit': 50000.0,
                'price_usd': 50000.0,
                'fee_usd': 10.0
            },
            {
                'date': datetime(2024, 2, 1),
                'type': 'sell',
                'symbol': 'BTC',
                'amount': 0.5,
                'price_per_unit': 60000.0,
                'price_usd': 30000.0,
                'fee_usd': 7.5
            }
        ]

        summary = calculator.calculate_taxes(transactions)

        assert summary['total_gain_loss'] == 5000.0  # (60000 - 50000) * 0.5
        assert len(calculator.lots) == 1  # Half remains
        assert calculator.lots[0].amount == 0.5

    def test_fifo_order(self):
        """Test that FIFO uses oldest lots first"""
        calculator = FIFOTaxCalculator()

        transactions = [
            {
                'date': datetime(2024, 1, 1),
                'type': 'buy',
                'symbol': 'BTC',
                'amount': 1.0,
                'price_per_unit': 40000.0,
                'price_usd': 40000.0,
                'fee_usd': 10.0
            },
            {
                'date': datetime(2024, 2, 1),
                'type': 'buy',
                'symbol': 'BTC',
                'amount': 1.0,
                'price_per_unit': 50000.0,
                'price_usd': 50000.0,
                'fee_usd': 10.0
            },
            {
                'date': datetime(2024, 3, 1),
                'type': 'sell',
                'symbol': 'BTC',
                'amount': 1.0,
                'price_per_unit': 60000.0,
                'price_usd': 60000.0,
                'fee_usd': 15.0
            }
        ]

        summary = calculator.calculate_taxes(transactions)

        # Should use first lot (40000), not second (50000)
        assert summary['total_gain_loss'] == 20000.0  # 60000 - 40000
        assert len(calculator.lots) == 1  # Second lot remains
        assert calculator.lots[0].price_per_unit == 50000.0

    def test_short_term_vs_long_term(self):
        """Test short-term vs long-term classification"""
        calculator = FIFOTaxCalculator()

        buy_date = datetime(2024, 1, 1)
        short_term_sale = buy_date + timedelta(days=200)  # < 365 days
        long_term_sale = buy_date + timedelta(days=400)  # > 365 days

        # Short-term transaction
        transactions_short = [
            {
                'date': buy_date,
                'type': 'buy',
                'symbol': 'BTC',
                'amount': 1.0,
                'price_per_unit': 50000.0,
                'price_usd': 50000.0,
                'fee_usd': 10.0
            },
            {
                'date': short_term_sale,
                'type': 'sell',
                'symbol': 'BTC',
                'amount': 0.5,
                'price_per_unit': 60000.0,
                'price_usd': 30000.0,
                'fee_usd': 7.5
            }
        ]

        summary = calculator.calculate_taxes(transactions_short)
        assert summary['num_short_term'] == 1
        assert summary['num_long_term'] == 0

        # Long-term transaction
        calculator = FIFOTaxCalculator()
        transactions_long = [
            {
                'date': buy_date,
                'type': 'buy',
                'symbol': 'BTC',
                'amount': 1.0,
                'price_per_unit': 50000.0,
                'price_usd': 50000.0,
                'fee_usd': 10.0
            },
            {
                'date': long_term_sale,
                'type': 'sell',
                'symbol': 'BTC',
                'amount': 1.0,
                'price_per_unit': 60000.0,
                'price_usd': 60000.0,
                'fee_usd': 15.0
            }
        ]

        summary = calculator.calculate_taxes(transactions_long)
        assert summary['num_short_term'] == 0
        assert summary['num_long_term'] == 1

    def test_multiple_lots_in_one_sale(self):
        """Test selling amount that spans multiple lots"""
        calculator = FIFOTaxCalculator()

        transactions = [
            {
                'date': datetime(2024, 1, 1),
                'type': 'buy',
                'symbol': 'BTC',
                'amount': 0.5,
                'price_per_unit': 40000.0,
                'price_usd': 20000.0,
                'fee_usd': 5.0
            },
            {
                'date': datetime(2024, 2, 1),
                'type': 'buy',
                'symbol': 'BTC',
                'amount': 0.5,
                'price_per_unit': 50000.0,
                'price_usd': 25000.0,
                'fee_usd': 6.25
            },
            {
                'date': datetime(2024, 3, 1),
                'type': 'sell',
                'symbol': 'BTC',
                'amount': 0.8,  # Spans both lots
                'price_per_unit': 60000.0,
                'price_usd': 48000.0,
                'fee_usd': 12.0
            }
        ]

        summary = calculator.calculate_taxes(transactions)

        # Should create 2 capital gain entries (one from each lot)
        assert summary['num_transactions'] == 2
        assert len(calculator.lots) == 1
        assert abs(calculator.lots[0].amount - 0.2) < 0.00000001  # 0.5 + 0.5 - 0.8


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, '-v'])


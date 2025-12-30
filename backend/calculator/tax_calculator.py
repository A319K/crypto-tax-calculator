from datetime import datetime
from collections import deque


class TaxLot:
    """
    Represents a single purchase (lot) of cryptocurrency.
    Used for tracking cost basis in FIFO calculations.
    """
    def __init__(self, date, amount, price_per_unit, symbol):
        self.date = date
        self.amount = amount  # Remaining amount in this lot
        self.original_amount = amount  # Original purchase amount
        self.price_per_unit = price_per_unit
        self.symbol = symbol
        self.cost_basis = amount * price_per_unit

    def __repr__(self):
        return f"TaxLot({self.date.date()}, {self.amount} {self.symbol} @ ${self.price_per_unit:.2f})"


class CapitalGain:
    """
    Represents a single capital gain/loss from a sale.
    """
    def __init__(self, sale_date, purchase_date, symbol, amount,
                 cost_basis, proceeds, gain_loss, term):
        self.sale_date = sale_date
        self.purchase_date = purchase_date
        self.symbol = symbol
        self.amount = amount
        self.cost_basis = cost_basis
        self.proceeds = proceeds
        self.gain_loss = gain_loss  # proceeds - cost_basis
        self.term = term  # 'short' or 'long'
        self.holding_days = (sale_date - purchase_date).days

    def __repr__(self):
        return f"CapitalGain({self.term.upper()}: ${self.gain_loss:.2f})"


class FIFOTaxCalculator:
    """
    Calculates capital gains and losses using FIFO (First In, First Out) method.
    """

    def __init__(self):
        self.lots = deque()  # Queue of purchase lots (FIFO)
        self.capital_gains = []  # List of all capital gains/losses
        self.errors = []  # Track any calculation errors

    def process_transaction(self, transaction):
        """
        Process a single transaction (buy or sell).

        Args:
            transaction (dict): Transaction data from parser
        """
        if transaction['type'] == 'buy':
            self._process_buy(transaction)
        elif transaction['type'] == 'sell':
            self._process_sell(transaction)
        else:
            self.errors.append(f"Unknown transaction type: {transaction['type']}")

    def _process_buy(self, transaction):
        """Add a new tax lot for a purchase."""
        lot = TaxLot(
            date=transaction['date'],
            amount=transaction['amount'],
            price_per_unit=transaction['price_per_unit'],
            symbol=transaction['symbol']
        )
        self.lots.append(lot)

    def _process_sell(self, transaction):
        """
        Process a sale by matching against oldest lots (FIFO).
        May need to use multiple lots if sale amount > single lot amount.
        """
        remaining_to_sell = transaction['amount']
        sale_date = transaction['date']
        sale_price_per_unit = transaction['price_per_unit']
        symbol = transaction['symbol']

        # Keep selling from oldest lots until we've sold the full amount
        while remaining_to_sell > 0.00000001:  # Use small epsilon for float comparison
            if not self.lots:
                self.errors.append(
                    f"Error: Trying to sell {remaining_to_sell} {symbol} "
                    f"but no lots available on {sale_date.date()}"
                )
                break

            # Get oldest lot (FIFO)
            oldest_lot = self.lots[0]

            # Check if this lot is for the same cryptocurrency
            if oldest_lot.symbol != symbol:
                self.errors.append(
                    f"Error: Symbol mismatch - trying to sell {symbol} "
                    f"but oldest lot is {oldest_lot.symbol}"
                )
                self.lots.popleft()
                continue

            # Determine how much to use from this lot
            amount_from_lot = min(remaining_to_sell, oldest_lot.amount)

            # Calculate cost basis for this portion
            cost_basis = amount_from_lot * oldest_lot.price_per_unit

            # Calculate proceeds from sale
            proceeds = amount_from_lot * sale_price_per_unit

            # Calculate gain/loss
            gain_loss = proceeds - cost_basis

            # Determine if short-term or long-term
            holding_days = (sale_date - oldest_lot.date).days
            term = 'long' if holding_days > 365 else 'short'

            # Create capital gain record
            capital_gain = CapitalGain(
                sale_date=sale_date,
                purchase_date=oldest_lot.date,
                symbol=symbol,
                amount=amount_from_lot,
                cost_basis=cost_basis,
                proceeds=proceeds,
                gain_loss=gain_loss,
                term=term
            )

            self.capital_gains.append(capital_gain)

            # Update lot and remaining amounts
            oldest_lot.amount -= amount_from_lot
            remaining_to_sell -= amount_from_lot

            # Remove lot if fully used
            if oldest_lot.amount < 0.00000001:  # Essentially zero
                self.lots.popleft()

    def calculate_taxes(self, transactions):
        """
        Calculate taxes for a list of transactions.

        Args:
            transactions (list): List of transaction dicts from parser

        Returns:
            dict: Tax summary with gains, losses, and breakdowns
        """
        # Reset state
        self.lots = deque()
        self.capital_gains = []
        self.errors = []

        # Sort transactions by date (important for FIFO)
        sorted_transactions = sorted(transactions, key=lambda t: t['date'])

        # Process each transaction
        for transaction in sorted_transactions:
            self.process_transaction(transaction)

        # Generate summary
        return self._generate_summary()

    def _generate_summary(self):
        """Generate summary report of all capital gains/losses."""
        if not self.capital_gains:
            return {
                'total_gain_loss': 0,
                'short_term_gain_loss': 0,
                'long_term_gain_loss': 0,
                'num_transactions': 0,
                'errors': self.errors
            }

        short_term_gains = [g for g in self.capital_gains if g.term == 'short']
        long_term_gains = [g for g in self.capital_gains if g.term == 'long']

        short_term_total = sum(g.gain_loss for g in short_term_gains)
        long_term_total = sum(g.gain_loss for g in long_term_gains)

        return {
            'total_gain_loss': short_term_total + long_term_total,
            'short_term_gain_loss': short_term_total,
            'long_term_gain_loss': long_term_total,
            'num_short_term': len(short_term_gains),
            'num_long_term': len(long_term_gains),
            'num_transactions': len(self.capital_gains),
            'capital_gains': self.capital_gains,
            'remaining_lots': list(self.lots),
            'errors': self.errors
        }

    def get_detailed_report(self):
        """Get detailed line-by-line report of all capital gains."""
        if not self.capital_gains:
            return "No capital gains to report."

        report = []
        report.append("=" * 80)
        report.append("DETAILED CAPITAL GAINS REPORT")
        report.append("=" * 80)
        report.append("")

        for i, gain in enumerate(self.capital_gains, 1):
            report.append(f"Transaction {i}:")
            report.append(f"  Sale Date: {gain.sale_date.date()}")
            report.append(f"  Purchase Date: {gain.purchase_date.date()}")
            report.append(f"  Holding Period: {gain.holding_days} days ({gain.term.upper()}-TERM)")
            report.append(f"  Amount: {gain.amount} {gain.symbol}")
            report.append(f"  Cost Basis: ${gain.cost_basis:,.2f}")
            report.append(f"  Proceeds: ${gain.proceeds:,.2f}")
            report.append(f"  Gain/Loss: ${gain.gain_loss:,.2f}")
            report.append("")

        return "\n".join(report)


# Test the calculator
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    from parsers.gemini_parser import GeminiParser

    print("=" * 80)
    print("FIFO TAX CALCULATOR - TEST RUN")
    print("=" * 80)
    print()

    # Parse transactions
    parser = GeminiParser('../sample_data/gemini_sample.csv')
    transactions = parser.parse()

    # Calculate taxes
    calculator = FIFOTaxCalculator()
    summary = calculator.calculate_taxes(transactions)

    # Display detailed report
    print(calculator.get_detailed_report())

    # Display summary
    print("=" * 80)
    print("TAX SUMMARY")
    print("=" * 80)
    print(f"Total Capital Gain/Loss: ${summary['total_gain_loss']:,.2f}")
    print(f"Short-term Gain/Loss: ${summary['short_term_gain_loss']:,.2f} ({summary['num_short_term']} transactions)")
    print(f"Long-term Gain/Loss: ${summary['long_term_gain_loss']:,.2f} ({summary['num_long_term']} transactions)")
    print()

    # Display remaining lots
    if summary['remaining_lots']:
        print("Remaining Crypto Holdings:")
        for lot in summary['remaining_lots']:
            print(f"  {lot.amount} {lot.symbol} purchased on {lot.date.date()} @ ${lot.price_per_unit:,.2f}")

    # Display any errors
    if summary['errors']:
        print()
        print("ERRORS:")
        for error in summary['errors']:
            print(f"  ⚠️  {error}")

    print("=" * 80)
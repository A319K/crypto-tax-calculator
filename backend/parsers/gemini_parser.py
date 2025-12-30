import pandas as pd
from datetime import datetime

class GeminiParser:
    """
    Parses Gemini CSV transaction files and converts them into
    structured transaction data for tax calculations.
    """

    def __init__(self, csv_path):
        """
        Initialize parser with path to CSV file.

        Args:
            csv_path (str): Path to Gemini CSV file
        """
        self.csv_path = csv_path
        self.transactions = []

    def parse(self):
        """
        Parse the CSV file and return structured transaction data.

        Returns:
            list: List of transaction dictionaries
        """
        # Read CSV using pandas
        df = pd.read_csv(self.csv_path)

        # Process each row
        for _, row in df.iterrows():
            # Combine date and time into single datetime object
            transaction_date = datetime.strptime(
                f"{row['Date']} {row['Time']}",
                "%Y-%m-%d %H:%M:%S"
            )

            # Create structured transaction
            transaction = {
                'date': transaction_date,
                'type': row['Type'].lower(),  # 'buy' or 'sell'
                'symbol': row['Symbol'],  # e.g., 'BTC'
                'amount': abs(float(row['BTC Amount'])),  # Quantity of crypto
                'price_usd': abs(float(row['USD Amount'])),  # Total USD value
                'fee_usd': float(row['Fee (USD)']),  # Transaction fee
                'price_per_unit': abs(float(row['USD Amount'])) / abs(float(row['BTC Amount']))  # Calculate unit price
            }

            self.transactions.append(transaction)

        return self.transactions

    def get_summary(self):
        """
        Get a summary of parsed transactions.

        Returns:
            dict: Summary statistics
        """
        if not self.transactions:
            return None

        buys = [t for t in self.transactions if t['type'] == 'buy']
        sells = [t for t in self.transactions if t['type'] == 'sell']

        return {
            'total_transactions': len(self.transactions),
            'total_buys': len(buys),
            'total_sells': len(sells),
            'total_spent': sum(t['price_usd'] for t in buys),
            'total_received': sum(t['price_usd'] for t in sells)
        }


# Test code - runs when you execute this file directly
if __name__ == "__main__":
    print("=" * 60)
    print("GEMINI CSV PARSER - TEST RUN")
    print("=" * 60)

    # Create parser instance
    parser = GeminiParser('../sample_data/gemini_sample.csv')

    # Parse transactions
    transactions = parser.parse()

    # Display results
    print(f"\n✅ Successfully parsed {len(transactions)} transactions:\n")

    for i, t in enumerate(transactions, 1):
        print(f"Transaction {i}:")
        print(f"  Date: {t['date']}")
        print(f"  Type: {t['type'].upper()}")
        print(f"  Amount: {t['amount']} {t['symbol']}")
        print(f"  Total USD: ${t['price_usd']:,.2f}")
        print(f"  Price per unit: ${t['price_per_unit']:,.2f}")
        print(f"  Fee: ${t['fee_usd']:.2f}")
        print()

    # Display summary
    summary = parser.get_summary()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Buys: {summary['total_buys']}")
    print(f"Total Sells: {summary['total_sells']}")
    print(f"Total Spent: ${summary['total_spent']:,.2f}")
    print(f"Total Received: ${summary['total_received']:,.2f}")
    print("=" * 60)
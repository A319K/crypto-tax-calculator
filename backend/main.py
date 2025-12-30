from parsers.gemini_parser import GeminiParser
from calculator.tax_calculator import FIFOTaxCalculator

def main():
    """
    Integration test: Parse CSV and calculate taxes end-to-end
    """
    print("=" * 80)
    print("🚀 CRYPTO TAX CALCULATOR - FULL INTEGRATION TEST")
    print("=" * 80)
    print()

    # Step 1: Parse CSV
    print("📄 Step 1: Parsing Gemini CSV file...")
    parser = GeminiParser('sample_data/gemini_sample.csv')
    transactions = parser.parse()
    print(f"✅ Parsed {len(transactions)} transactions")
    print()

    # Show transaction summary
    summary = parser.get_summary()
    print("Transaction Summary:")
    print(f"  - Total Buys: {summary['total_buys']}")
    print(f"  - Total Sells: {summary['total_sells']}")
    print(f"  - Total Spent: ${summary['total_spent']:,.2f}")
    print(f"  - Total Received: ${summary['total_received']:,.2f}")
    print()

    # Step 2: Calculate taxes
    print("💰 Step 2: Calculating capital gains using FIFO method...")
    calculator = FIFOTaxCalculator()
    tax_summary = calculator.calculate_taxes(transactions)
    print(f"✅ Calculated {tax_summary['num_transactions']} capital gain/loss events")
    print()

    # Step 3: Display detailed report
    print(calculator.get_detailed_report())

    # Step 4: Display tax summary
    print("=" * 80)
    print("📊 TAX SUMMARY FOR IRS REPORTING")
    print("=" * 80)
    print()
    print(f"Total Capital Gain/Loss:     ${tax_summary['total_gain_loss']:>12,.2f}")
    print(f"  Short-term (<= 365 days):  ${tax_summary['short_term_gain_loss']:>12,.2f}")
    print(f"  Long-term (> 365 days):    ${tax_summary['long_term_gain_loss']:>12,.2f}")
    print()
    print(f"Number of taxable events:    {tax_summary['num_transactions']:>12}")
    print(f"  Short-term transactions:   {tax_summary['num_short_term']:>12}")
    print(f"  Long-term transactions:    {tax_summary['num_long_term']:>12}")
    print()

    # Step 5: Show remaining holdings
    if tax_summary['remaining_lots']:
        print("=" * 80)
        print("💎 REMAINING CRYPTO HOLDINGS (Unrealized)")
        print("=" * 80)
        print()
        total_value = 0
        for lot in tax_summary['remaining_lots']:
            print(f"  {lot.amount:.8f} {lot.symbol}")
            print(f"    Purchased: {lot.date.date()}")
            print(f"    Cost Basis: ${lot.price_per_unit:,.2f} per unit")
            print(f"    Total Cost: ${lot.cost_basis:,.2f}")
            print()
            total_value += lot.cost_basis
        print(f"Total Unrealized Cost Basis: ${total_value:,.2f}")
        print()

    # Step 6: Show any errors
    if tax_summary['errors']:
        print("=" * 80)
        print("⚠️  ERRORS DETECTED")
        print("=" * 80)
        for error in tax_summary['errors']:
            print(f"  {error}")
        print()

    print("=" * 80)
    print("✅ CALCULATION COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Review the capital gains report above")
    print("  2. Report short-term gains as ordinary income on Form 1040")
    print("  3. Report long-term gains on Schedule D")
    print("  4. Keep this report for your tax records")
    print()
    print("⚠️  DISCLAIMER: This is for educational purposes only.")
    print("    Please consult a tax professional for official tax advice.")
    print("=" * 80)


if __name__ == "__main__":
    main()
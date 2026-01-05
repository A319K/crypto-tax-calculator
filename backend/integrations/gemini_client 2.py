import requests
import json
import base64
import hmac
import hashlib
import time
from datetime import datetime
from typing import List, Dict, Optional

class GeminiAPIClient:
    """Client for fetching transaction data from Gemini API"""

    def __init__(self, api_key: str, api_secret: str, sandbox: bool = False):
        """Initialize the Gemini API client

        Args:
            api_key: Gemini API key
            api_secret: Gemini API secret
            sandbox: If true, use the Sandbox API
        """
        self.api_key = api_key
        self.api_secret = api_secret.encode()

        if sandbox: self.base_url = "https://sandbox.gemini.com"
        else: self.base_url = "https://api.gemini.com"

    def _generate_signature(self, payload: dict) -> tuple:
        """Generate HMAC-SHA384 signature for request

        Returns:
            tuple: (base64_payload, signature)
        """
        #Convert payload to JSON and encode
        encoded_payload = json.dumps(payload).encode()

        #Base64 encode the payload
        b64_payload = base64.b64encode(encoded_payload)

        #Create HMAC-SHA364 signature
        signature = hmac.new(self.api_secret, b64_payload, hashlib.sha384)

        return b64_payload.decode(), signature

    def _make_request(self, endpoint: str, payload: dict) -> dict:
        """Make authenticated request to Gemini API

        Args:
            endpoint: API endpoint
            payload: request payload

        Returns:
            dict: API response
        """
        url = f"{self.base_url}{endpoint}"

        #Add timestamp nonce to payload
        payload['nonce'] = int(time.time() * 1000) # milliseconds
        payload['request'] = endpoint

        #Generate signature
        b64_payload, signature = self._generate_signature(payload)

        #Build headers
        headers = {
            'Content-Type': "text/plain",
            'Content-Length': "0",
            'X-GEMINI-APIKEY': self.api_key,
            'X-GEMINI-PAYLOAD': b64_payload,
            'X-GEMINI-SIGNATURE': signature,
            'Cache-Control': "no-cache"
        }

        #make request
        response = requests.post(url, headers=headers)
        response.raise_for_status()    #Raise exception for bad status codes
        return response.json()

    def get_past_trades(self, symbol: str = "btcusd", limit: int = 500) -> List[Dict]:
        """Fetch past trades from Gemini

        Args:
            symbol: Trading pair symbol
            limit: Max number of trades to fetch (default 500, max 500)

        Returns:
            List of trade dictionaries
        """
        payload = {
            "symbol": symbol.lower(),
            "limit_trades": min(limit, 500)
        }

        return self._make_request("/v1/mytrades", payload)

    def get_balances(self) -> List[Dict]:
        """
        Get account balnces for all currencies

        Returns:
           List of balance dictionaries
        """

        return self._make_request("/v1/balances", {})

    def test_connection(self) -> bool:
        """
        Test if API credentials are valid

        Returns:
            bool: true if connection successful
        """

        try:
            self.get_balances()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def convert_to_parser_format(self, trades: List[Dict], symbol: str = "BTC") -> List[Dict]:
        """Convert Gemini API response to the format expected by tax calculator

        Gemini API returns trades like:
        {
            "timestamp": 1577836800,
            "timestampms": 1577836800000,
            "tid": 12345678,
            "price": "7000.00",
            "amount": "0.01",
            "exchange": "gemini",
            "type": "Buy",  # or "Sell"
            "fee_currency": "USD",
            "fee_amount": "0.70",
            "broken": false,
            "is_auction_fill": false,
            "is_clearing_fill": false,
            "symbol": "BTCUSD"
        }

        Args:
            trades: List of trades from Gemini API
            symbol: Crypto symbol
        Returns:
            List of transactions in parser format
        """

        converted = []

        for trade in trades:
            #Convert timestamp to datetime
            timestamp = datetime.fromtimestamp(trade["timestampms"])

            #Determine transaction type
            tx_type = trade["type"].lower() #"buy" or "sell"

            #Extract amounts and prices
            amount = float(trade["amount"])
            price_usd = float(trade["price"]) * amount
            fee_usd = float(trade.get('fee_amount', 0))
            price_per_unit = float(trade['price'])

            transaction = {
                'date': timestamp,
                'type': tx_type,
                'symbol': symbol,
                'amount': amount,
                'price_usd': price_usd,
                'price_per_unit': price_per_unit,
                'fee_usd': fee_usd,
                'trade_id': trade.get('tid', None),
                'exchange': 'gemini'
            }

            converted.append(transaction)

        #Sort by date with oldest first
        converted.sort(key=lambda x: x['date'])

        return converted
if __name__ == "__main__":
    import os

    #For testing, set these environment variables or use test keys
    API_KEY = os.getenv("GEMINI_API_KEY", 'test_key')
    API_SECRET = os.getenv("GEMINI_API_SECRET", 'test_secret')

    #Use sandbox for testing
    client = GeminiAPIClient(API_KEY, API_SECRET, sandbox = True)

    #Test connection
    print("Testing connection...")
    if client.test_connection():
        print("Connection test passed")

        #Fetch trades
        print("\nFetching past trades...")
        trades = client._get_past_trades("btcusd", limit = 10)
        print(f"Fetched {len(trades)} trades")

        #Convert to parser format
        converted = client.convert_to_parser_format(trades)
        print(f"Converted {len(converted)} trades")

        #Display first trade
        if converted:
            print("\nFirst transaction:")
            print(f" Date: {converted[0]['date']}")
            print(f" Type: {converted[0]['type']}")
            print(f" Amount: {converted[0]['amount']} {converted[0]['symbol']}")
            print(f" Price: ${converted[0]['price_usd']:,.2f}")
        else:
            print("Connection failed")
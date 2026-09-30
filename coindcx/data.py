import requests
import pandas as pd
from datetime import datetime, timezone


class CoinDCXMarketData:
    """
    CoinDCX public market-data API (No API key is required.).    

    Covers:
        - Market details
        - Available symbols/pairs
        - Ticker
        - OHLCV candles
        - Recent trades
        - Order book
    """

    BASE_URL = "https://api.coindcx.com"

    def __init__(self, timeout=10):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "CoinDCXDataCollector/1.0"
        })
        self.timeout = timeout

        self._markets = None

    # ============================================================
    # Internal helpers
    # ============================================================

    def _get(self, endpoint, params=None):
        """Send a GET request and return JSON response."""
        url = f"{self.BASE_URL}{endpoint}"

        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout
        )

        response.raise_for_status()
        return response.json()

    def _fetch_market_details(self):
        """Fetch and cache CoinDCX market details."""
        if self._markets is None:
            self._markets = self._get(
                "/exchange/v1/markets_details"
            )

        return self._markets

    # ============================================================
    # Market information
    # ============================================================

    def get_market_details(self, symbol=None):
        """
        Get market details.

        symbol=None:
            Return details of all markets.

        symbol="BTCUSDT":
            Return details of that symbol.
        """
        markets = self._fetch_market_details()

        if symbol is None:
            return markets

        symbol = symbol.upper()

        for market in markets:
            if market["symbol"].upper() == symbol:
                return market

        return None

    def get_available_symbols(self):
        """Return all available symbols."""
        markets = self._fetch_market_details()

        return [
            market["symbol"]
            for market in markets
        ]

    def get_available_pairs(self):
        """Return all available CoinDCX pairs."""
        markets = self._fetch_market_details()

        return [
            market["pair"]
            for market in markets
        ]

    def find_market(self, symbol):
        """
        Find market information using symbol.

        Example:
            find_market("BTCUSDT")
        """
        return self.get_market_details(symbol)

    # ============================================================
    # Ticker
    # ============================================================

    def get_tickers(self):
        """Get ticker information for all markets."""
        return self._get("/exchange/ticker")

    def get_ticker(self, symbol):
        """
        Get ticker for a particular symbol.

        Example:
            get_ticker("BTCUSDT")
        """
        symbol = symbol.upper()

        tickers = self.get_tickers()

        for ticker in tickers:
            if ticker.get("market", "").upper() == symbol:
                return ticker

        return None

    # ============================================================
    # Candles / OHLCV
    # ============================================================

    def get_candles(
        self,
        pair,
        interval="1m",
        start_time=None,
        end_time=None,
        limit=1000,
        dataframe=True
    ):
        """
        Get OHLCV candle data.

        Parameters
        ----------
        pair : str
            Example: "B-BTC_USDT"

        interval : str
            "1m", "15m", "1h", "1d"

        start_time : int
            Unix timestamp in milliseconds.

        end_time : int
            Unix timestamp in milliseconds.

        limit : int
            Maximum 1000.

        dataframe : bool
            Return pandas DataFrame if True.
        """

        params = {
            "pair": pair,
            "interval": interval,
            "limit": min(limit, 1000)
        }

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        data = self._get(
            "/market_data/candles",
            params=params
        )

        if not dataframe:
            return data

        df = pd.DataFrame(data)

        if df.empty:
            return df

        df["time"] = pd.to_datetime(
            df["time"],
            unit="ms",
            utc=True
        )

        df = df.sort_values("time")
        df = df.reset_index(drop=True)

        return df

    # ============================================================
    # Recent trades
    # ============================================================

    def get_trades(
        self,
        pair,
        limit=500,
        dataframe=True
    ):
        """
        Get recent trades for a pair.

        Example:
            get_trades("B-BTC_USDT")
        """

        params = {
            "pair": pair,
            "limit": limit
        }

        data = self._get(
            "/market_data/trade_history",
            params=params
        )

        if not dataframe:
            return data

        return pd.DataFrame(data)

    # ============================================================
    # Order book
    # ============================================================

    def get_orderbook(
        self,
        pair,
        depth=50
    ):
        """
        Get current order book.

        depth:
            1, 5, 10, 20, 50, 100, 200
        """

        params = {
            "pair": pair,
            "depth": depth
        }

        return self._get(
            "/market_data/orderbook",
            params=params
        )

    # ============================================================
    # Convenience functions
    # ============================================================

    def symbol_to_pair(self, symbol):
        """
        Convert symbol to CoinDCX pair.

        Example:
            BTCUSDT -> B-BTC_USDT
        """

        market = self.find_market(symbol)

        if market is None:
            raise ValueError(
                f"Symbol '{symbol}' not found."
            )

        return market["pair"]

    def get_candles_for_symbol(
        self,
        symbol,
        interval="1m",
        start_time=None,
        end_time=None,
        limit=1000
    ):
        """Get candles using symbol instead of pair."""

        pair = self.symbol_to_pair(symbol)

        return self.get_candles(
            pair=pair,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )

    def get_orderbook_for_symbol(
        self,
        symbol,
        depth=50
    ):
        """Get order book using symbol."""

        pair = self.symbol_to_pair(symbol)

        return self.get_orderbook(
            pair=pair,
            depth=depth
        )

    def get_trades_for_symbol(
        self,
        symbol,
        limit=500
    ):
        """Get trades using symbol."""

        pair = self.symbol_to_pair(symbol)

        return self.get_trades(
            pair=pair,
            limit=limit
        )
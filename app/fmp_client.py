import os
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

FMP_API_KEY = os.getenv("FMP_API_KEY")
FMP_BASE_URL = os.getenv("FMP_BASE_URL", "https://financialmodelingprep.com/stable")

if not FMP_API_KEY:
    raise RuntimeError(
        "FMP_API_KEY is not set. Please configure it in your environment or .env file."
    )

class FMPClient:
    """
    Thin wrapper over Financial Modeling Prep stable endpoints.

    Base: https://financialmodelingprep.com/stable
    Examples:
      - /search-symbol?query=AAPL&apikey=...
      - /income-statement?symbol=AAPL&period=annual&limit=5&apikey=...
    """

    def __init__(self, api_key: str = FMP_API_KEY, base_url: str = FMP_BASE_URL) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        endpoint: e.g. 'search-symbol', 'income-statement', 'profile'
        """
        if params is None:
            params = {}
        params["apikey"] = self.api_key

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        resp = requests.get(url, params=params, timeout=10)

        if not resp.ok:
            raise RuntimeError(
                f"FMP API error: {resp.status_code} {resp.text[:200]}"
            )
        return resp.json()

    def search_symbol(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        https://financialmodelingprep.com/stable/search-symbol?query=...&limit=...&exchange=...
        """
        return self._get(
            "search-symbol",
            {
                "query": query,
                "limit": limit,
                # you can adjust or drop the exchange filter
                "exchange": "NASDAQ,NYSE,AMEX",
            },
        )

    def get_company_profile(self, symbol: str) -> List[Dict[str, Any]]:
        """
        https://financialmodelingprep.com/stable/profile?symbol=AAPL
        """
        return self._get(
            "profile",
            {"symbol": symbol.upper()},
        )

    def get_income_statement(
        self,
        symbol: str,
        period: str = "annual",
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        https://financialmodelingprep.com/stable/income-statement?symbol=AAPL&period=annual&limit=5
        """
        return self._get(
            "income-statement",
            {
                "symbol": symbol.upper(),
                "period": period,
                "limit": limit,
            },
        )

    def get_balance_sheet(
        self,
        symbol: str,
        period: str = "annual",
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        https://financialmodelingprep.com/stable/balance-sheet-statement?symbol=AAPL&period=annual&limit=5
        """
        return self._get(
            "balance-sheet-statement",
            {
                "symbol": symbol.upper(),
                "period": period,
                "limit": limit,
            },
        )

    def get_cash_flow(
        self,
        symbol: str,
        period: str = "annual",
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        https://financialmodelingprep.com/stable/cash-flow-statement?symbol=AAPL&period=annual&limit=5
        """
        return self._get(
            "cash-flow-statement",
            {
                "symbol": symbol.upper(),
                "period": period,
                "limit": limit,
            },
        )

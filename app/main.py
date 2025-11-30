from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from app.fmp_client import FMPClient
from app.schemas import (
    CompanySearchItem,
    CompanySearchResponse,
    CompanySnapshot,
    IncomeSnapshot,
    BalanceSheetSnapshot,
    CashFlowSnapshot,
    HistoryPoint,
    CompanyHistoryResponse,
)


app = FastAPI(
    title="Company Fundamentals Microservice",
    version="0.1.0",
    description=(
        "Minimal open-source service that wraps Financial Modeling Prep "
        "stable fundamentals endpoints."
    ),
)


def get_client() -> FMPClient:
    return FMPClient()


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}

@app.get(
    "/companies/search",
    response_model=CompanySearchResponse,
    summary="Search for companies by name or symbol",
)
def search_companies(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    client: FMPClient = Depends(get_client),
):
    raw = client.search_symbol(q, limit=limit)
    results: List[CompanySearchItem] = []

    for item in raw:
        results.append(
            CompanySearchItem(
                symbol=item.get("symbol"),
                name=item.get("name") or item.get("companyName"),
                exchange=item.get("stockExchange"),
                currency=item.get("currency"),
            )
        )

    return CompanySearchResponse(results=results)

@app.get(
    "/companies/{symbol}/snapshot",
    response_model=CompanySnapshot,
    summary="Latest fundamentals snapshot for a given company",
)
def company_snapshot(
    symbol: str,
    client: FMPClient = Depends(get_client),
):
    profiles = client.get_company_profile(symbol)
    if not profiles:
        raise HTTPException(status_code=404, detail="Company profile not found")

    profile = profiles[0]
    name = profile.get("companyName") or profile.get("name")
    currency = profile.get("currency")
    exchange = profile.get("exchangeShortName") or profile.get("exchange")

    income_list = client.get_income_statement(symbol, period="annual", limit=1)
    balance_list = client.get_balance_sheet(symbol, period="annual", limit=1)
    cashflow_list = client.get_cash_flow(symbol, period="annual", limit=1)

    income_raw = income_list[0] if income_list else {}
    balance_raw = balance_list[0] if balance_list else {}
    cashflow_raw = cashflow_list[0] if cashflow_list else {}

    as_of = (
        income_raw.get("date")
        or balance_raw.get("date")
        or cashflow_raw.get("date")
    )

    income = IncomeSnapshot(
        revenue=income_raw.get("revenue") or income_raw.get("revenueTTM"),
        netIncome=income_raw.get("netIncome") or income_raw.get("netIncomeTTM"),
    )

    balance = BalanceSheetSnapshot(
        totalAssets=balance_raw.get("totalAssets"),
        totalLiabilities=balance_raw.get("totalLiabilities"),
    )

    cashflow = CashFlowSnapshot(
        operatingCashFlow=cashflow_raw.get("operatingCashFlow")
        or cashflow_raw.get("operatingCashFlowTTM")
    )

    snapshot = CompanySnapshot(
        symbol=str(symbol).upper(),
        name=name,
        currency=currency,
        exchange=exchange,
        asOf=as_of,
        income=income,
        balanceSheet=balance,
        cashFlow=cashflow,
    )

    return snapshot


@app.get(
    "/companies/{symbol}/history",
    response_model=CompanyHistoryResponse,
    summary="Simple revenue/net income history for charting",
)
def company_history(
    symbol: str,
    years: int = Query(5, ge=1, le=20),
    client: FMPClient = Depends(get_client),
):
    income_list = client.get_income_statement(
        symbol, period="annual", limit=years
    )

    if not income_list:
        raise HTTPException(status_code=404, detail="No income statement data found")

    points: List[HistoryPoint] = []
    for row in income_list:
        points.append(
            HistoryPoint(
                date=row.get("date"),
                revenue=row.get("revenue"),
                netIncome=row.get("netIncome"),
            )
        )

    return CompanyHistoryResponse(symbol=str(symbol).upper(), points=points)

@app.exception_handler(RuntimeError)
def runtime_error_handler(request, exc: RuntimeError):
    return JSONResponse(
        status_code=502,
        content={"detail": str(exc)},
    )

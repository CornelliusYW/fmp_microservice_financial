from typing import List, Optional
from pydantic import BaseModel, Field

class CompanySearchItem(BaseModel):
    symbol: str
    name: str
    exchange: Optional[str] = None
    currency: Optional[str] = None

class CompanySearchResponse(BaseModel):
    results: List[CompanySearchItem]

class IncomeSnapshot(BaseModel):
    revenue: Optional[float] = Field(
        None, description="Total revenue for the period"
    )
    netIncome: Optional[float] = Field(
        None, description="Net income for the period"
    )

class BalanceSheetSnapshot(BaseModel):
    totalAssets: Optional[float] = None
    totalLiabilities: Optional[float] = None

class CashFlowSnapshot(BaseModel):
    operatingCashFlow: Optional[float] = None

class CompanySnapshot(BaseModel):
    symbol: str
    name: Optional[str] = None
    currency: Optional[str] = None
    exchange: Optional[str] = None
    asOf: Optional[str] = Field(
        None, description="Financial statement date"
    )

    income: IncomeSnapshot
    balanceSheet: BalanceSheetSnapshot
    cashFlow: CashFlowSnapshot

class HistoryPoint(BaseModel):
    date: str
    revenue: Optional[float] = None
    netIncome: Optional[float] = None

class CompanyHistoryResponse(BaseModel):
    symbol: str
    points: List[HistoryPoint]

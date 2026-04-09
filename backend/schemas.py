"""
EF Report Studio — Pydantic Schemas
Handles the conversion between the frontend's nested JSON and the flat DB rows.
"""

from __future__ import annotations
import json
from typing import Optional
from pydantic import BaseModel


# ════════════════════════════════════════════════
# Sub-models matching frontend JSON shape exactly
# ════════════════════════════════════════════════

class PersonInfo(BaseModel):
    name: str = ""
    dob: str = ""
    age: int | str = ""
    ssnLast4: str = ""


class Financials(BaseModel):
    monthlySalary: float = 0
    expenseBudget: float = 0
    insuranceDeductibles: float = 0
    privateReserveTarget: float = 0


class Liability(BaseModel):
    type: str
    rate: float = 0


class RetirementAccounts(BaseModel):
    client1: list[str] = []
    client2: list[str] = []


class Trust(BaseModel):
    address: str = ""


class Accounts(BaseModel):
    retirement: RetirementAccounts = RetirementAccounts()
    nonRetirement: list[str] = []
    trust: Trust = Trust()
    liabilities: list[Liability] = []


# ════════════════════════════════════════════════
# Client schemas
# ════════════════════════════════════════════════

class ClientIn(BaseModel):
    """Incoming client data from frontend — same shape as the JS object."""
    id: Optional[int] = None
    type: str = "single"
    client1: PersonInfo = PersonInfo()
    client2: PersonInfo = PersonInfo()
    financials: Financials = Financials()
    accounts: Accounts = Accounts()
    lastReportDate: Optional[str] = None


class ClientOut(ClientIn):
    """Outgoing client data — same shape but always has an id."""
    id: int


# ════════════════════════════════════════════════
# Report schemas
# ════════════════════════════════════════════════

class ReportIn(BaseModel):
    """Incoming report data from the Generate Report page."""
    clientId: Optional[int] = None
    clientName: Optional[str] = None
    clientType: Optional[str] = None
    client1: Optional[dict] = None
    client2: Optional[dict] = None

    # SACS
    inflow: float = 0
    outflow: float = 0
    excess: float = 0
    prBalance: float = 0
    schwabBalance: float = 0
    prTarget: float = 0

    # TCC
    retirementC1: list[dict] = []
    retirementC1Total: float = 0
    retirementC2: list[dict] = []
    retirementC2Total: float = 0
    nonRetirement: list[dict] = []
    nonRetirementTotal: float = 0
    trustAddress: str = ""
    trustValue: float = 0
    liabilities: list[dict] = []
    liabilitiesTotal: float = 0
    grandTotal: float = 0

    class Config:
        extra = "allow"  # Allow extra fields like c1_ret_0, nr_0, etc.


class ReportOut(BaseModel):
    """Outgoing report data."""
    id: int
    clientId: int
    date: str
    data: dict  # Full report snapshot


# ════════════════════════════════════════════════
# Conversion helpers: DB row ↔ Nested JSON
# ════════════════════════════════════════════════

def client_row_to_dict(row) -> dict:
    """Convert a flat Client DB row into the nested JSON the frontend expects."""
    return {
        "id": row.id,
        "type": row.type,
        "client1": {
            "name": row.client1_name or "",
            "dob": row.client1_dob or "",
            "age": row.client1_age or "",
            "ssnLast4": row.client1_ssn_last4 or "",
        },
        "client2": {
            "name": row.client2_name or "",
            "dob": row.client2_dob or "",
            "age": row.client2_age or "",
            "ssnLast4": row.client2_ssn_last4 or "",
        },
        "financials": {
            "monthlySalary": row.monthly_salary or 0,
            "expenseBudget": row.expense_budget or 0,
            "insuranceDeductibles": row.insurance_deductibles or 0,
            "privateReserveTarget": row.private_reserve_target or 0,
        },
        "accounts": {
            "retirement": {
                "client1": _parse_json(row.retirement_c1),
                "client2": _parse_json(row.retirement_c2),
            },
            "nonRetirement": _parse_json(row.non_retirement),
            "trust": {
                "address": row.trust_address or "",
            },
            "liabilities": _parse_json(row.liabilities),
        },
        "lastReportDate": row.last_report_date,
    }


def client_dict_to_row_kwargs(data: ClientIn) -> dict:
    """Convert a nested ClientIn schema into flat kwargs for the Client model."""
    return {
        "type": data.type,
        "client1_name": data.client1.name,
        "client1_dob": data.client1.dob,
        "client1_age": int(data.client1.age) if data.client1.age != "" else 0,
        "client1_ssn_last4": data.client1.ssnLast4,
        "client2_name": data.client2.name,
        "client2_dob": data.client2.dob,
        "client2_age": int(data.client2.age) if data.client2.age != "" else 0,
        "client2_ssn_last4": data.client2.ssnLast4,
        "monthly_salary": data.financials.monthlySalary,
        "expense_budget": data.financials.expenseBudget,
        "insurance_deductibles": data.financials.insuranceDeductibles,
        "private_reserve_target": data.financials.privateReserveTarget,
        "retirement_c1": json.dumps(data.accounts.retirement.client1),
        "retirement_c2": json.dumps(data.accounts.retirement.client2),
        "non_retirement": json.dumps(data.accounts.nonRetirement),
        "trust_address": data.accounts.trust.address,
        "liabilities": json.dumps([l.model_dump() for l in data.accounts.liabilities]),
        "last_report_date": data.lastReportDate,
    }


def report_row_to_dict(row) -> dict:
    """Convert a Report DB row to the frontend-expected JSON."""
    data = _parse_json(row.report_data)
    data["id"] = row.id
    data["date"] = row.date
    return data


def _parse_json(text: str) -> list | dict:
    """Safely parse a JSON string, returning [] on failure."""
    if not text:
        return []
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return []

"""
EF Report Studio — Database Seed Script
Populates the 6 mock clients from the PRD.
Can be run as:  python -m backend.seed
Or auto-runs on first startup if DB is empty.
"""

import json
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import Client
from backend.database import SessionLocal, init_db


SEED_CLIENTS = [
    {
        "type": "married",
        "client1_name": "John Doe",
        "client1_dob": "1980-05-15",
        "client1_age": 45,
        "client1_ssn_last4": "1234",
        "client2_name": "Jane Doe",
        "client2_dob": "1982-03-20",
        "client2_age": 43,
        "client2_ssn_last4": "5678",
        "monthly_salary": 15000,
        "expense_budget": 11000,
        "insurance_deductibles": 5000,
        "private_reserve_target": 71000,
        "retirement_c1": json.dumps(["IRA", "Roth IRA"]),
        "retirement_c2": json.dumps(["Roth IRA", "401K"]),
        "non_retirement": json.dumps(["Brokerage", "Joint Account"]),
        "trust_address": "123 Main St, Atlanta, GA",
        "liabilities": json.dumps([{"type": "Mortgage", "rate": 4.5}, {"type": "Auto Loan", "rate": 3.2}]),
        "last_report_date": "2026-03-25",
    },
    {
        "type": "single",
        "client1_name": "Alice Smith",
        "client1_dob": "1975-08-10",
        "client1_age": 50,
        "client1_ssn_last4": "9876",
        "client2_name": "",
        "client2_dob": "",
        "client2_age": 0,
        "client2_ssn_last4": "",
        "monthly_salary": 12000,
        "expense_budget": 8000,
        "insurance_deductibles": 3500,
        "private_reserve_target": 51500,
        "retirement_c1": json.dumps(["IRA", "401K"]),
        "retirement_c2": json.dumps([]),
        "non_retirement": json.dumps(["Brokerage"]),
        "trust_address": "456 Oak St, Dallas, TX",
        "liabilities": json.dumps([{"type": "Mortgage", "rate": 5.0}]),
        "last_report_date": "2026-04-01",
    },
    {
        "type": "single",
        "client1_name": "Bob Johnson",
        "client1_dob": "1988-11-02",
        "client1_age": 38,
        "client1_ssn_last4": "1111",
        "client2_name": "",
        "client2_dob": "",
        "client2_age": 0,
        "client2_ssn_last4": "",
        "monthly_salary": 18000,
        "expense_budget": 12000,
        "insurance_deductibles": 4200,
        "private_reserve_target": 76200,
        "retirement_c1": json.dumps(["Roth IRA", "Pension"]),
        "retirement_c2": json.dumps([]),
        "non_retirement": json.dumps(["Brokerage", "Savings"]),
        "trust_address": "",
        "liabilities": json.dumps([{"type": "Mortgage", "rate": 3.5}, {"type": "Other Loan", "rate": 6.0}]),
        "last_report_date": "2026-03-15",
    },
    {
        "type": "married",
        "client1_name": "Michael Brown",
        "client1_dob": "1965-04-12",
        "client1_age": 60,
        "client1_ssn_last4": "2222",
        "client2_name": "Sarah Brown",
        "client2_dob": "1968-09-25",
        "client2_age": 57,
        "client2_ssn_last4": "3333",
        "monthly_salary": 25000,
        "expense_budget": 15000,
        "insurance_deductibles": 6000,
        "private_reserve_target": 96000,
        "retirement_c1": json.dumps(["IRA", "401K"]),
        "retirement_c2": json.dumps(["Roth IRA", "401K"]),
        "non_retirement": json.dumps(["Joint Account", "Savings", "Brokerage"]),
        "trust_address": "789 Pine Ln, Seattle, WA",
        "liabilities": json.dumps([{"type": "Mortgage", "rate": 2.9}]),
        "last_report_date": "2026-02-28",
    },
    {
        "type": "single",
        "client1_name": "Emma Wilson",
        "client1_dob": "1992-07-08",
        "client1_age": 33,
        "client1_ssn_last4": "4444",
        "client2_name": "",
        "client2_dob": "",
        "client2_age": 0,
        "client2_ssn_last4": "",
        "monthly_salary": 9500,
        "expense_budget": 6000,
        "insurance_deductibles": 2800,
        "private_reserve_target": 38800,
        "retirement_c1": json.dumps(["401K"]),
        "retirement_c2": json.dumps([]),
        "non_retirement": json.dumps(["Savings"]),
        "trust_address": "",
        "liabilities": json.dumps([{"type": "Auto Loan", "rate": 5.5}]),
        "last_report_date": "2026-01-10",
    },
    {
        "type": "married",
        "client1_name": "Robert Chen",
        "client1_dob": "1970-02-14",
        "client1_age": 56,
        "client1_ssn_last4": "5555",
        "client2_name": "Linda Chen",
        "client2_dob": "1972-11-30",
        "client2_age": 53,
        "client2_ssn_last4": "6666",
        "monthly_salary": 22000,
        "expense_budget": 14000,
        "insurance_deductibles": 5500,
        "private_reserve_target": 89500,
        "retirement_c1": json.dumps(["IRA", "Roth IRA", "401K"]),
        "retirement_c2": json.dumps(["Roth IRA"]),
        "non_retirement": json.dumps(["Joint Account", "Brokerage"]),
        "trust_address": "321 Peachtree Rd, Atlanta, GA",
        "liabilities": json.dumps([{"type": "Mortgage", "rate": 3.8}, {"type": "Auto Loan", "rate": 4.1}]),
        "last_report_date": "2026-03-10",
    },
]


def seed_clients(db: Session):
    """Insert the 6 mock clients into the database."""
    now = datetime.utcnow().isoformat()
    for data in SEED_CLIENTS:
        data["created_at"] = now
        client = Client(**data)
        db.add(client)
    db.commit()


if __name__ == "__main__":
    # Direct execution: python -m backend.seed
    init_db()
    db = SessionLocal()
    try:
        count = db.query(Client).count()
        if count > 0:
            print(f"⚠️  Database already has {count} clients. Skipping seed.")
        else:
            seed_clients(db)
            print("✅ Seeded 6 mock clients successfully!")
    finally:
        db.close()

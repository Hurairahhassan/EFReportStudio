"""
EF Report Studio — SQLAlchemy ORM Models
"""

from sqlalchemy import Column, Integer, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Text, nullable=False, default="single")  # "single" or "married"

    # Client 1
    client1_name = Column(Text, nullable=False)
    client1_dob = Column(Text, default="")
    client1_age = Column(Integer, default=0)
    client1_ssn_last4 = Column(Text, default="")

    # Client 2 (spouse — nullable for single clients)
    client2_name = Column(Text, default="")
    client2_dob = Column(Text, default="")
    client2_age = Column(Integer, default=0)
    client2_ssn_last4 = Column(Text, default="")

    # Financials
    monthly_salary = Column(Float, default=0)
    expense_budget = Column(Float, default=0)
    insurance_deductibles = Column(Float, default=0)
    private_reserve_target = Column(Float, default=0)

    # Accounts (stored as JSON text)
    retirement_c1 = Column(Text, default="[]")       # JSON array: ["IRA","Roth IRA"]
    retirement_c2 = Column(Text, default="[]")       # JSON array
    non_retirement = Column(Text, default="[]")      # JSON array
    trust_address = Column(Text, default="")
    liabilities = Column(Text, default="[]")         # JSON array: [{"type":"Mortgage","rate":4.5}]

    # Metadata
    last_report_date = Column(Text, nullable=True)
    created_at = Column(Text, default="")

    # Relationship
    reports = relationship("Report", back_populates="client", cascade="all, delete-orphan")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    date = Column(Text, nullable=False)         # ISO date: "2026-04-10"
    report_data = Column(Text, default="{}")    # Full JSON snapshot of all report values
    created_at = Column(Text, default="")

    # Relationship
    client = relationship("Client", back_populates="reports")

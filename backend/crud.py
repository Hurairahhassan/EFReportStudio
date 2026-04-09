"""
EF Report Studio — CRUD Operations
All database read/write operations.
"""

import json
from datetime import date, datetime
from sqlalchemy.orm import Session

from backend.models import Client, Report
from backend.schemas import (
    ClientIn,
    client_dict_to_row_kwargs,
    client_row_to_dict,
    report_row_to_dict,
)


# ════════════════════════════════════════════════
# Clients
# ════════════════════════════════════════════════

def get_clients(db: Session) -> list[dict]:
    rows = db.query(Client).order_by(Client.id).all()
    return [client_row_to_dict(r) for r in rows]


def get_client(db: Session, client_id: int) -> dict | None:
    row = db.query(Client).filter(Client.id == client_id).first()
    if not row:
        return None
    return client_row_to_dict(row)


def create_client(db: Session, data: ClientIn) -> dict:
    kwargs = client_dict_to_row_kwargs(data)
    kwargs["created_at"] = datetime.utcnow().isoformat()
    row = Client(**kwargs)
    db.add(row)
    db.commit()
    db.refresh(row)
    return client_row_to_dict(row)


def update_client(db: Session, client_id: int, data: ClientIn) -> dict | None:
    row = db.query(Client).filter(Client.id == client_id).first()
    if not row:
        return None
    kwargs = client_dict_to_row_kwargs(data)
    for key, value in kwargs.items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return client_row_to_dict(row)


def delete_client(db: Session, client_id: int) -> bool:
    row = db.query(Client).filter(Client.id == client_id).first()
    if not row:
        return False
    db.delete(row)  # Cascades to reports
    db.commit()
    return True


# ════════════════════════════════════════════════
# Reports
# ════════════════════════════════════════════════

def get_reports(db: Session, client_id: int) -> list[dict]:
    rows = (
        db.query(Report)
        .filter(Report.client_id == client_id)
        .order_by(Report.id.desc())
        .all()
    )
    return [report_row_to_dict(r) for r in rows]


def get_latest_report(db: Session, client_id: int) -> dict | None:
    row = (
        db.query(Report)
        .filter(Report.client_id == client_id)
        .order_by(Report.id.desc())
        .first()
    )
    if not row:
        return None
    return report_row_to_dict(row)


def create_report(db: Session, client_id: int, report_data: dict) -> dict:
    today_str = date.today().isoformat()

    report = Report(
        client_id=client_id,
        date=today_str,
        report_data=json.dumps(report_data),
        created_at=datetime.utcnow().isoformat(),
    )
    db.add(report)

    # Update client lastReportDate
    client = db.query(Client).filter(Client.id == client_id).first()
    if client:
        client.last_report_date = today_str

    db.commit()
    db.refresh(report)
    return report_row_to_dict(report)


# ════════════════════════════════════════════════
# Dashboard Stats
# ════════════════════════════════════════════════

def get_stats(db: Session) -> dict:
    from datetime import timedelta

    clients = db.query(Client).all()
    total_clients = len(clients)

    # Reports this quarter
    now = date.today()
    quarter_start = date(now.year, ((now.month - 1) // 3) * 3 + 1, 1)
    reports_this_quarter = (
        db.query(Report)
        .filter(Report.date >= quarter_start.isoformat())
        .count()
    )

    # Clients needing a report (no report in 90+ days)
    ninety_days_ago = (now - timedelta(days=90)).isoformat()
    needs_report = 0
    for c in clients:
        if not c.last_report_date or c.last_report_date < ninety_days_ago:
            needs_report += 1

    # Recent activity
    recent_reports = (
        db.query(Report)
        .order_by(Report.id.desc())
        .limit(10)
        .all()
    )
    activity = []
    for r in recent_reports:
        client = db.query(Client).filter(Client.id == r.client_id).first()
        if client:
            name = (
                f"{client.client1_name} & {client.client2_name}"
                if client.type == "married"
                else client.client1_name
            )
            activity.append({"name": name, "date": r.date, "clientId": client.id})

    return {
        "totalClients": total_clients,
        "reportsThisQuarter": reports_this_quarter,
        "needsReport": needs_report,
        "recentActivity": activity,
    }

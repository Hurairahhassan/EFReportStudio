"""
EF Report Studio — FastAPI Application
API routes + static file serving for single-server deployment.
"""

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.database import init_db, get_db
from backend.schemas import ClientIn, ReportIn
from backend import crud

# ════════════════════════════════════════════════
# App Setup
# ════════════════════════════════════════════════

app = FastAPI(
    title="EF Report Studio API",
    description="Backend for the EF Financial Planning client report portal",
    version="1.0.0",
)

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()
    # Auto-seed if database is empty
    from backend.database import SessionLocal
    db = SessionLocal()
    try:
        from backend.models import Client
        count = db.query(Client).count()
        if count == 0:
            from backend.seed import seed_clients
            seed_clients(db)
            print("✅ Database seeded with 6 mock clients")
        else:
            print(f"✅ Database ready — {count} clients found")
    finally:
        db.close()


# ════════════════════════════════════════════════
# API Routes — Clients
# ════════════════════════════════════════════════

@app.get("/api/clients")
def list_clients(db: Session = Depends(get_db)):
    return crud.get_clients(db)


@app.get("/api/clients/{client_id}")
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@app.post("/api/clients")
def create_client(data: ClientIn, db: Session = Depends(get_db)):
    return crud.create_client(db, data)


@app.put("/api/clients/{client_id}")
def update_client(client_id: int, data: ClientIn, db: Session = Depends(get_db)):
    result = crud.update_client(db, client_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Client not found")
    return result


@app.delete("/api/clients/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    success = crud.delete_client(db, client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"ok": True}


# ════════════════════════════════════════════════
# API Routes — Reports
# ════════════════════════════════════════════════

@app.get("/api/clients/{client_id}/reports")
def list_reports(client_id: int, db: Session = Depends(get_db)):
    return crud.get_reports(db, client_id)


@app.get("/api/clients/{client_id}/reports/latest")
def get_latest_report(client_id: int, db: Session = Depends(get_db)):
    report = crud.get_latest_report(db, client_id)
    if not report:
        return None
    return report


@app.post("/api/clients/{client_id}/reports")
def create_report(client_id: int, data: ReportIn, db: Session = Depends(get_db)):
    # Verify client exists
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return crud.create_report(db, client_id, data.model_dump())


# ════════════════════════════════════════════════
# API Routes — Dashboard Stats
# ════════════════════════════════════════════════

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    return crud.get_stats(db)


# ════════════════════════════════════════════════
# Static File Serving — Frontend
# ════════════════════════════════════════════════

# Serve static assets (CSS, JS)
STATIC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/css", StaticFiles(directory=os.path.join(STATIC_DIR, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(STATIC_DIR, "js")), name="js")


# HTML page routes — serve each page directly
@app.get("/")
def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/index.html")
def serve_index_html():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/clients.html")
def serve_clients():
    return FileResponse(os.path.join(STATIC_DIR, "clients.html"))


@app.get("/add-client.html")
def serve_add_client():
    return FileResponse(os.path.join(STATIC_DIR, "add-client.html"))


@app.get("/edit-client.html")
def serve_edit_client():
    return FileResponse(os.path.join(STATIC_DIR, "edit-client.html"))


@app.get("/generate-report.html")
def serve_generate_report():
    return FileResponse(os.path.join(STATIC_DIR, "generate-report.html"))


@app.get("/report-preview.html")
def serve_report_preview():
    return FileResponse(os.path.join(STATIC_DIR, "report-preview.html"))

"""
main.py — FastAPI application entry point.

Exposes:
  POST /api/generate   — Run full pipeline (extract → chart → PDF)
  GET  /api/reports    — List all generated PDFs
  GET  /api/reports/{filename} — Download a PDF
  DELETE /api/reports/{filename} — Delete a PDF
  GET  /api/stats      — Live metrics for dashboard

APScheduler runs the pipeline automatically at 06:00 UTC Mon-Fri.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import OUTPUTS_DIR, TEMP_DIR, CRON_EXPRESSION, REPORT_FOOTER
from data_processor import DataProcessor
from chart_generator import generate_bar_chart, generate_line_chart
from pdf_generator import PDFReport

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    HAS_SCHEDULER = True
except ImportError:
    HAS_SCHEDULER = False

processor = DataProcessor()
scheduler = None

router = APIRouter(prefix="/api")


# ── Helpers ────────────────────────────────────────────────

def _run_pipeline() -> dict:
    stats = processor.compute_stats()
    source_summary = processor.get_source_summary()
    time_series = processor.get_time_series()

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    bar_path = TEMP_DIR / f"chart_bar_{ts}.png"
    line_path = TEMP_DIR / f"chart_line_{ts}.png"

    generate_bar_chart(source_summary.to_dict(orient="records"), bar_path)
    generate_line_chart(time_series.to_dict(orient="records"), line_path)

    pdf_name = f"reporte_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    pdf_path = OUTPUTS_DIR / pdf_name

    PDFReport(pdf_path).generate(stats, bar_path, line_path)

    for p in [bar_path, line_path]:
        if p.exists():
            p.unlink()

    return {
        "status": "ok",
        "filename": pdf_name,
        "path": str(pdf_path),
        "stats": stats,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def _reports_list() -> list[dict]:
    files = []
    if not OUTPUTS_DIR.exists():
        return files
    for f in sorted(OUTPUTS_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if f.suffix.lower() == ".pdf":
            stat = f.stat()
            files.append({
                "filename": f.name,
                "size_bytes": stat.st_size,
                "size_kb": round(stat.st_size / 1024, 1),
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            })
    return files


# ── Internal pipeline (for scheduler) ──────────────────────

def scheduled_pipeline():
    try:
        _run_pipeline()
    except Exception as e:
        print(f"[SCHEDULER] Pipeline failed: {e}")


# ── Lifespan ───────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    if HAS_SCHEDULER:
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            scheduled_pipeline,
            CronTrigger.from_crontab(CRON_EXPRESSION),
            id="auto_pipeline",
            name="AutoData daily pipeline",
            replace_existing=True,
        )
        scheduler.start()
        print(f"[SCHEDULER] Started with cron: {CRON_EXPRESSION}")
    yield
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)


app = FastAPI(
    title="AutoData Pipeline API",
    version="3.2.1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints ──────────────────────────────────────────────

@router.post("/generate", summary="Ejecuta el pipeline completo")
def generate_report():
    try:
        result = _run_pipeline()
        return JSONResponse(content=result, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports", summary="Lista los PDFs generados")
def list_reports():
    return JSONResponse(content=_reports_list())


@router.get("/reports/{filename}", summary="Descarga un PDF específico")
def download_report(filename: str):
    filepath = OUTPUTS_DIR / filename
    if not filepath.exists() or not filepath.is_file():
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return FileResponse(
        path=str(filepath),
        media_type="application/pdf",
        filename=filename,
    )


@router.delete("/reports/{filename}", summary="Elimina un PDF")
def delete_report(filename: str):
    filepath = OUTPUTS_DIR / filename
    if not filepath.exists() or not filepath.is_file():
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    try:
        filepath.unlink()
        return JSONResponse(content={"status": "deleted", "filename": filename})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")


@router.get("/stats", summary="Métricas en vivo para el dashboard")
def get_stats():
    try:
        stats = processor.compute_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(router)


# ── Direct execution ───────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

"""Vercel Serverless Function — self-contained pipeline API."""
import os, sys, traceback, json
from pathlib import Path

os.environ.setdefault("MATPLOTLIB_BACKEND", "Agg")

backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
sys.path.insert(0, backend_dir)

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DataStream Engine API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

errors = []

try:
    import pandas as pd
    import numpy as np
except Exception as e:
    errors.append(f"pandas/numpy: {e}")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import seaborn as sns
except Exception as e:
    errors.append(f"matplotlib/seaborn: {e}")

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        Image, PageBreak, HRFlowable
    )
except Exception as e:
    errors.append(f"reportlab: {e}")

try:
    from data_processor import DataProcessor
    from chart_generator import generate_bar_chart, generate_line_chart
    from pdf_generator import PDFReport
    from config import OUTPUTS_DIR, TEMP_DIR
except Exception as e:
    errors.append(f"local modules: {e}")

if errors:
    @app.get("/api/ping")
    async def ping_error():
        return PlainTextResponse("\n".join(errors))
else:
    from datetime import datetime
    from fastapi import APIRouter

    processor = DataProcessor()
    router = APIRouter(prefix="/api")

    def _run_pipeline():
        stats = processor.compute_stats()
        ss = processor.get_source_summary()
        ts = processor.get_time_series()
        ts_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        bp = TEMP_DIR / f"chart_bar_{ts_str}.png"
        lp = TEMP_DIR / f"chart_line_{ts_str}.png"
        generate_bar_chart(ss.to_dict(orient="records"), bp)
        generate_line_chart(ts.to_dict(orient="records"), lp)
        pdf_name = f"reporte_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
        pdf_path = OUTPUTS_DIR / pdf_name
        PDFReport(pdf_path).generate(stats, bp, lp)
        for p in [bp, lp]:
            if p.exists(): p.unlink()
        return {"status": "ok", "filename": pdf_name, "path": str(pdf_path),
                "stats": stats, "generated_at": datetime.utcnow().isoformat() + "Z"}

    def _reports_list():
        files = []
        if OUTPUTS_DIR.exists():
            for f in sorted(OUTPUTS_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
                if f.suffix.lower() == ".pdf":
                    s = f.stat()
                    files.append({"filename": f.name, "size_bytes": s.st_size,
                                  "size_kb": round(s.st_size / 1024, 1),
                                  "created_at": datetime.fromtimestamp(s.st_ctime).isoformat()})
        return files

    @router.post("/generate")
    def generate():
        try:
            return JSONResponse(content=_run_pipeline(), status_code=201)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/reports")
    def list_reports():
        return JSONResponse(content=_reports_list())

    @router.get("/reports/{filename}")
    def download(filename: str):
        fp = OUTPUTS_DIR / filename
        if not fp.exists():
            raise HTTPException(404, "Reporte no encontrado")
        return FileResponse(str(fp), media_type="application/pdf", filename=filename)

    @router.delete("/reports/{filename}")
    def delete(filename: str):
        fp = OUTPUTS_DIR / filename
        if not fp.exists():
            raise HTTPException(404, "Reporte no encontrado")
        fp.unlink()
        return JSONResponse(content={"status": "deleted", "filename": filename})

    @router.get("/stats")
    def stats():
        try:
            return JSONResponse(content=processor.compute_stats())
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(router)

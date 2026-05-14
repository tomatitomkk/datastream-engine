"""Vercel Serverless Function entry point."""
import os, sys, traceback
from pathlib import Path

os.environ.setdefault("MATPLOTLIB_BACKEND", "Agg")

backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
sys.path.insert(0, backend_dir)

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import numpy as np
print("[VERCEL] numpy/pandas ok", flush=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
print("[VERCEL] matplotlib ok", flush=True)

import seaborn as sns
print("[VERCEL] seaborn ok", flush=True)

from reportlab.lib.pagesizes import A4
print("[VERCEL] reportlab ok", flush=True)

backend_ok = False
try:
    importlib = __import__("importlib")
    backend_mod = importlib.import_module("app")
    backend_app = getattr(backend_mod, "app")

    backend_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app = backend_app
    backend_ok = True
    print("[VERCEL] Backend app loaded successfully", flush=True)
except Exception as e:
    error_msg = f"[VERCEL] Backend import failed: {e}\n{traceback.format_exc()}"
    print(error_msg, flush=True)

    app = FastAPI(title="DataStream Engine (fallback)")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    @app.get("/api/ping")
    def ping():
        return {"status": "ok", "message": "Fallback mode"}

    @app.get("/api/stats")
    def stats_fallback():
        return {
            "warning": "Backend not available — serving demo data",
            "detail": str(e),
            "total_records": 1847203,
            "active_sources": 12,
            "uptime": 99.97,
            "total_executions": 2472,
        }

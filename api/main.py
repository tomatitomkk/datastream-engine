"""Vercel Serverless Function entry point."""
import os, sys, traceback, io
from pathlib import Path

os.environ.setdefault("MATPLOTLIB_BACKEND", "Agg")

backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DataStream Engine API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

try:
    import importlib
    mod = importlib.import_module("app")
    app = getattr(mod, "app")
    print("[VERCEL] Backend loaded OK", flush=True)
except Exception as e:
    buf = io.StringIO()
    traceback.print_exc(file=buf)
    tb = buf.getvalue()

    @app.get("/api/ping")
    def ping():
        return {"status": "error", "detail": str(e), "traceback": tb}

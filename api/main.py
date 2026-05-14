"""Vercel Serverless Function entry point."""
import os, sys, traceback
from pathlib import Path

os.environ.setdefault("MATPLOTLIB_BACKEND", "Agg")

backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DataStream Engine API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

try:
    import importlib
    mod = importlib.import_module("app")
    app = getattr(mod, "app")
    print("[VERCEL] Backend loaded OK", flush=True)
except Exception as e:
    tb = traceback.format_exc()

    @app.get("/api/ping")
    async def ping():
        return PlainTextResponse(f"ERROR: {e}\n\n{tb}")

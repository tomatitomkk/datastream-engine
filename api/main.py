"""Vercel Serverless Function entry point."""
import os, sys, traceback
from pathlib import Path

os.environ.setdefault("MATPLOTLIB_BACKEND", "Agg")

backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
sys.path.insert(0, backend_dir)

# Define app at top level so Vercel can detect it
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DataStream Engine API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

try:
    import importlib
    mod = importlib.import_module("app")
    app = getattr(mod, "app")
    print("[VERCEL] Backend app loaded successfully", flush=True)
except Exception as e:
    print(f"[VERCEL] Backend import failed: {e}", flush=True)
    traceback.print_exc()

    @app.get("/api/ping")
    def ping():
        return {"status": "ok", "message": "Fallback — backend modules failed to load"}

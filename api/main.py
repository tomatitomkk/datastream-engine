"""
Vercel Serverless Function entry point.
Wraps the FastAPI application and mounts under /api/ prefix.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from fastapi import FastAPI
from main import app as backend_app

app = FastAPI(title="DataStream Engine API (Vercel)", version="3.2.1")
app.mount("/api", backend_app)

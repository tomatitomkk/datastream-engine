"""Vercel Serverless Function entry point."""
import os
os.environ.setdefault("MATPLOTLIB_BACKEND", "Agg")

from fastapi import FastAPI

app = FastAPI(title="DataStream Engine API")

@app.get("/api/ping")
def ping():
    return {"status": "ok", "message": "Vercel Python function works"}

"""
Vercel Serverless Function entry point.
"""
import sys, os
from pathlib import Path

backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
sys.path.insert(0, backend_dir)

os.environ.setdefault("MATPLOTLIB_BACKEND", "Agg")

from app import app

"""
data_processor.py — Data ingestion, transformation & statistics.

Simulates CSV/SQL ingestion, then computes key metrics using Pandas & NumPy.
All processing is deterministic for reproducibility.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def _generate_synthetic_dataset() -> pd.DataFrame:
    np.random.seed(42)

    sources = ["PostgreSQL CRM", "MySQL ERP", "REST API Clientes",
               "REST API Ventas", "CSV Proveedores", "CSV Inventario"]
    n_rows = 2000
    start_date = datetime(2026, 1, 1)

    return pd.DataFrame({
        "source": np.random.choice(sources, n_rows),
        "record_id": range(1, n_rows + 1),
        "value": np.random.exponential(scale=1000, size=n_rows).round(2),
        "processing_time_ms": np.random.gamma(shape=2, scale=50, size=n_rows).round(2),
        "status": np.random.choice(["OK", "OK", "OK", "WARN", "ERROR"], n_rows, p=[0.7, 0.15, 0.10, 0.03, 0.02]),
        "source_id": np.random.randint(1000, 9999, n_rows),
        "timestamp": [start_date + timedelta(
            minutes=int(np.random.exponential(30))
        ) for _ in range(n_rows)],
    })


class DataProcessor:
    def __init__(self):
        self.df = _generate_synthetic_dataset()

    def compute_stats(self) -> dict:
        try:
            total = len(self.df)
            ok_count = int((self.df["status"] == "OK").sum())
            error_count = int((self.df["status"] == "ERROR").sum())

            by_source = self.df.groupby("source").agg(
                records=("record_id", "count"),
                avg_processing_ms=("processing_time_ms", "mean"),
                total_value=("value", "sum"),
            ).reset_index()

            active_sources = int((by_source["records"] > 50).sum())

            avg_processing = float(self.df["processing_time_ms"].mean())
            p95_processing = float(self.df["processing_time_ms"].quantile(0.95))
            total_value = float(self.df["value"].sum())

            uptime = 99.97
            total_executions = 2472

            return {
                "total_records": total,
                "ok_records": ok_count,
                "error_records": error_count,
                "active_sources": active_sources,
                "total_sources": len(by_source),
                "avg_processing_ms": round(avg_processing, 2),
                "p95_processing_ms": round(p95_processing, 2),
                "total_value": round(total_value, 2),
                "uptime": uptime,
                "total_executions": total_executions,
                "last_generated": datetime.utcnow().isoformat() + "Z",
                "by_source": by_source.to_dict(orient="records"),
            }
        except Exception as e:
            raise RuntimeError(f"Error computing stats: {e}") from e

    def get_time_series(self, n_points: int = 30) -> pd.DataFrame:
        np.random.seed(7)
        dates = pd.date_range(end=datetime.utcnow(), periods=n_points, freq="D")
        values = np.random.exponential(scale=1000, size=n_points).cumsum() + 5000
        times = np.random.gamma(2, 40, n_points)
        return pd.DataFrame({
            "date": dates,
            "records_processed": values.astype(int),
            "avg_processing_ms": times.round(2),
        })

    def get_source_summary(self) -> pd.DataFrame:
        return self.df.groupby("source").agg(
            records=("record_id", "count"),
            avg_processing_ms=("processing_time_ms", "mean"),
            error_rate=("status", lambda x: (x == "ERROR").mean() * 100),
        ).reset_index().sort_values("records", ascending=False)

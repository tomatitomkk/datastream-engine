import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
TEMP_DIR = BASE_DIR / "temp"

os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

CRON_EXPRESSION = "0 6 * * 1-5"

REPORT_FOOTER = "Arquitectura, diseno y desarrollo integral liderado por Dylan Ramirez Lopez"

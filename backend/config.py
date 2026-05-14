import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Try project-local dirs first; if read-only (Vercel), fall back to /tmp
_OUTPUTS = BASE_DIR / "outputs"
_TEMP = BASE_DIR / "temp"

try:
    os.makedirs(_OUTPUTS, exist_ok=True)
    os.makedirs(_TEMP, exist_ok=True)
    # Verify writability
    test = _OUTPUTS / ".write_test"
    test.touch(); test.unlink()
    OUTPUTS_DIR, TEMP_DIR = _OUTPUTS, _TEMP
except (OSError, PermissionError):
    OUTPUTS_DIR = Path("/tmp/outputs")
    TEMP_DIR = Path("/tmp/temp")
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

CRON_EXPRESSION = "0 6 * * 1-5"
REPORT_FOOTER = "Arquitectura, diseno y desarrollo integral liderado por Dylan Ramirez Lopez"

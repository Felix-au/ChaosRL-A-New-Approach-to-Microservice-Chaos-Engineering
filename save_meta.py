import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
import psutil
import torch
import numpy
import scipy
import sklearn

packages = {
    "torch": torch.__version__,
    "numpy": numpy.__version__,
    "scipy": scipy.__version__,
    "scikit-learn": sklearn.__version__,
    "psutil": psutil.__version__,
    "pandas": "disabled_by_smart_app_control_policy",
}

meta = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "os": platform.platform(),
    "system": platform.system(),
    "release": platform.release(),
    "machine": platform.machine(),
    "processor": platform.processor(),
    "cpu_count_logical": psutil.cpu_count(logical=True),
    "cpu_count_physical": psutil.cpu_count(logical=False),
    "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
    "ram_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
    "python_version": sys.version,
    "packages": packages,
}

Path("results").mkdir(parents=True, exist_ok=True)
with open("results/run_metadata.json", "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2)

print("Saved results/run_metadata.json successfully.")


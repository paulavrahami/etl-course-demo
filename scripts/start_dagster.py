"""Start Dagster after creating its local home directory."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = os.environ.copy()
env.setdefault("DAGSTER_HOME", str(ROOT / ".dagster_home"))
env.setdefault("WAREHOUSE_PATH", str(ROOT / "warehouse.duckdb"))
Path(env["DAGSTER_HOME"]).mkdir(parents=True, exist_ok=True)
raise SystemExit(subprocess.call(
    [sys.executable, "-m", "dagster", "dev", "-f", "orchestration/definitions.py"],
    cwd=ROOT, env=env,
))

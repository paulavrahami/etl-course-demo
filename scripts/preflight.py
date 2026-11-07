"""Run the classroom demo and check that Python and dbt agree."""
import argparse
import os
import shutil
import sqlite3
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    print("\n+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-only", action="store_true", help="Skip LanceDB and embedding model checks")
    parser.add_argument("--fake-embeddings", action="store_true", help="Test plumbing only; does not test semantic retrieval")
    args = parser.parse_args()
    py = sys.executable
    warmup = [py, "scripts/warmup.py"]
    if args.core_only:
        warmup.append("--core-only")
    elif args.fake_embeddings:
        warmup.append("--skip-model-download")
    run(warmup)
    for filename in ("customers.csv", "orders.csv", "products.csv", "reviews.json"):
        if not (ROOT / "data" / "raw" / filename).exists():
            raise SystemExit("Missing source data. Run python scripts/generate_data.py first.")
    run([py, "pipelines/01_pure_python_etl.py"])
    run([py, "pipelines/02_dlt_pipeline.py", "--offline"])
    run([py, "pipelines/02_dlt_pipeline.py", "--offline"])
    dbt = Path(py).with_name("dbt.exe" if os.name == "nt" else "dbt")
    dbt_command = str(dbt) if dbt.exists() else shutil.which("dbt")
    if not dbt_command:
        raise SystemExit("dbt executable not found in the active Python environment.")
    run([dbt_command, "build", "--profiles-dir", "."], cwd=ROOT / "dbt_project")
    import duckdb
    with sqlite3.connect(ROOT / "warehouse_basic.db") as basic, duckdb.connect(str(ROOT / "warehouse.duckdb"), read_only=True) as warehouse:
        n_basic = basic.execute("select count(*) from orders").fetchone()[0]
        n_dbt = warehouse.execute("select count(*) from marts.fct_orders").fetchone()[0]
        rev_basic = basic.execute("select sum(amount) from orders where status='paid'").fetchone()[0]
        rev_dbt = warehouse.execute("select sum(amount) from marts.fct_orders where status='paid'").fetchone()[0]
        if n_basic != n_dbt or abs(Decimal(str(rev_basic)) - Decimal(str(rev_dbt))) > Decimal("0.01"):
            raise SystemExit(f"Python/dbt mismatch: rows {n_basic}/{n_dbt}, revenue {rev_basic}/{rev_dbt}")
        print(f"OK Python/dbt agree: {n_dbt} valid orders; paid revenue={rev_dbt}")
    run([py, "-c", "import dagster as dg; from orchestration.definitions import defs; dg.Definitions.validate_loadable(defs); print('OK Dagster definitions and dependencies')"])
    if not args.core_only:
        extra = ["--fake-embeddings"] if args.fake_embeddings else []
        run([py, "pipelines/03_rag_pipeline.py", *extra])
        run([py, "pipelines/03_rag_pipeline.py", *extra])
        run([py, "pipelines/03_rag_pipeline.py", "--query", "תוך כמה זמן אפשר להחזיר מוצר אלקטרוני?", *extra])
    if args.core_only:
        print("\nבדיקת הליבה עברה. RAG לא נכלל בבדיקה זו.")
    elif args.fake_embeddings:
        print("\nזרימת הנתונים עברה עם וקטורים מדומים. איכות החיפוש הסמנטי לא נבדקה.")
    else:
        print("\nההדגמה עברה. בדקו גם את רלוונטיות המקורות שהחיפוש החזיר.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from None

"""
מודול 4 - אורקסטרציה עם Dagster
=================================
מחברים את כל החלקים לגרף אחד של "נכסי נתונים" (Software-Defined Assets):

  raw/customers, raw/orders, raw/products   (dlt)
            │
            ▼
  stg_* ──► fct_orders ──► dim_customers / mart_daily_revenue   (dbt; בדיקות dbt = asset checks)

  kb_vector_index   (RAG: docs -> chunks -> embeddings -> LanceDB)

הרצה:
    dagster dev -f orchestration/definitions.py
    ואז לפתוח http://localhost:3000 -> Assets -> Materialize all
"""
import importlib.util
import os
import sys
from pathlib import Path

import dagster as dg
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets

ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault("WAREHOUSE_PATH", str(ROOT / "warehouse.duckdb"))
os.environ.setdefault("DAGSTER_HOME", str(ROOT / ".dagster_home"))
Path(os.environ["DAGSTER_HOME"]).mkdir(parents=True, exist_ok=True)


def _load_module(filename: str):
    """הקבצים ב-pipelines/ מתחילים בספרה, אז טוענים אותם לפי נתיב."""
    path = ROOT / "pipelines" / filename
    module_name = f"shop_il_{path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    # dlt uses inspect.getmodule while its resource decorators execute.
    # Register the module before execution, as a normal Python import does.
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise
    return module


# ------------------------------------------------------------- Ingestion (dlt)
RAW_TABLES = ["customers", "orders", "products"]


@dg.multi_asset(
    specs=[dg.AssetSpec(["raw", t], group_name="ingestion", kinds={"dlt", "duckdb"}) for t in RAW_TABLES],
)
def raw_shop_tables(context: dg.AssetExecutionContext):
    dlt_module = _load_module("02_dlt_pipeline.py")
    offline = os.getenv("GITHUB_OFFLINE", "1") == "1"
    _, load_info = dlt_module.run_pipeline(offline=offline)
    context.log.info(str(load_info))
    for t in RAW_TABLES:
        load_id = load_info.loads_ids[-1] if load_info.loads_ids else "no new load"
        yield dg.MaterializeResult(asset_key=["raw", t], metadata={"load_id": load_id})


# ---------------------------------------------------------- Transform (dbt)
dbt_project = DbtProject(project_dir=ROOT / "dbt_project", profiles_dir=ROOT / "dbt_project")
dbt_project.prepare_if_dev()  # מריץ dbt parse אוטומטית ב-dagster dev


@dbt_assets(manifest=dbt_project.manifest_path)
def shop_dbt_assets(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    # sources של dbt (raw.customers וכו') ממופים אוטומטית לנכסים ["raw", "<table>"] שלמעלה
    yield from dbt.cli(["build"], context=context).stream()


# ------------------------------------------------------------- AI / RAG
@dg.asset(group_name="ai", kinds={"lancedb"})
def kb_vector_index(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """אינדוקס אינקרמנטלי של מסמכי הידע ל-Vector DB."""
    rag = _load_module("03_rag_pipeline.py")
    stats = rag.index_documents(rag.Embedder(fake=os.getenv("FAKE_EMBEDDINGS") == "1"))
    context.log.info(f"index stats: {stats}")
    return dg.MaterializeResult(metadata=stats)


# ------------------------------------------------------------- Scheduling
daily_job = dg.define_asset_job("daily_etl", selection=dg.AssetSelection.all())

defs = dg.Definitions(
    assets=[raw_shop_tables, shop_dbt_assets, kb_vector_index],
    resources={"dbt": DbtCliResource(project_dir=dbt_project)},
    jobs=[daily_job],
    schedules=[dg.ScheduleDefinition(job=daily_job, cron_schedule="0 6 * * *",
                                     execution_timezone="Asia/Jerusalem")],
)

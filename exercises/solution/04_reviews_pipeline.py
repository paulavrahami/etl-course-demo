"""
תרגיל כיתה - שלב 1: Extract & Load של ביקורות לקוחות עם dlt   [פתרון]
הרצה: python pipelines/04_reviews_pipeline.py
"""
import json
from pathlib import Path

import dlt

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
WAREHOUSE = ROOT / "warehouse.duckdb"


# replace: הקובץ הוא snapshot מלא. כפילויות נשארות ב-raw ומטופלות ב-dbt (שכבת staging).
@dlt.resource(name="reviews", write_disposition="replace")
def reviews():
    with open(RAW / "reviews.json", encoding="utf-8") as f:
        yield json.load(f)


def main() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="shop_il_reviews",
        pipelines_dir=str(ROOT / ".dlt" / "pipelines"),
        destination=dlt.destinations.duckdb(str(WAREHOUSE)),
        dataset_name="raw",
    )
    print(pipeline.run(reviews()))
    # שימו לב: product.id הפך לעמודה product__id, והרשימה tags הפכה לטבלת-בת reviews__tags
    with pipeline.sql_client() as c:
        print("reviews:", c.execute_sql("select count(*) from raw.reviews")[0][0])
        print("reviews__tags:", c.execute_sql("select count(*) from raw.reviews__tags")[0][0])


if __name__ == "__main__":
    main()

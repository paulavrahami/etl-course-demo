"""
תרגיל כיתה - שלב 1: Extract & Load של ביקורות לקוחות עם dlt
=============================================================
המשימה: לטעון את data/raw/reviews.json לסכמה raw ב-warehouse.duckdb, לטבלה בשם reviews.

רמזים:
  * הסתכלו איך customers() בנוי ב-pipelines/02_dlt_pipeline.py
  * הקובץ הוא snapshot מלא - איזה write_disposition מתאים?
  * אל תנקו כאן כלום! כפילויות ולכלוך נשארים ב-raw. ניקוי = dbt.

הרצה:     python pipelines/04_reviews_pipeline.py
בדיקה:    python exercises/check_exercise.py 1
"""
import json
from pathlib import Path

import dlt

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
WAREHOUSE = ROOT / "warehouse.duckdb"


# TODO 1: הוסיפו דקורטור @dlt.resource עם name ו-write_disposition מתאימים
def reviews():
    # TODO 2: פתחו את reviews.json ו-yield את רשימת הביקורות
    ...


def main() -> None:
    # TODO 3: צרו pipeline (pipeline_name="shop_il_reviews", destination duckdb לקובץ WAREHOUSE,
    #         dataset_name="raw", pipelines_dir=str(ROOT / ".dlt" / "pipelines"))
    #         והריצו אותו על reviews()
    ...

    # שאלה למחשבה: אחרי ההרצה, בדקו אילו טבלאות נוצרו. מה קרה לשדה product.id? ולרשימה tags?


if __name__ == "__main__":
    main()

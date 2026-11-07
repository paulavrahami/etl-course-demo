"""
תרגיל כיתה - שלב 4: מהמחסן ל-Vector DB
=========================================
המשימה:
  1. לקרוא את הביקורות הנקיות מ-staging.stg_reviews (+ שם המוצר מ-staging.stg_products)
  2. ליצור embedding לכל ביקורת ולטעון ל-LanceDB, טבלה בשם reviews, עם העמודות:
     review_id, product_id, product_name, rating, review_text, vector
  3. לחפש "על מה לקוחות מתלוננים?" - רק בביקורות עם rating <= 2

הרצה:  python pipelines/05_reviews_rag.py
       python pipelines/05_reviews_rag.py --query "על מה לקוחות מתלוננים?"
בדיקה: python exercises/check_exercise.py 4
"""
import argparse
import importlib.util
from pathlib import Path

import duckdb
import lancedb

ROOT = Path(__file__).resolve().parent.parent
WAREHOUSE = ROOT / "warehouse.duckdb"
DB_DIR = ROOT / "lancedb"
TABLE = "reviews"

# שימוש חוזר ב-Embedder מהמודול של ה-RAG (מוכן, לא צריך לגעת)
_spec = importlib.util.spec_from_file_location("rag", ROOT / "pipelines" / "03_rag_pipeline.py")
rag = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rag)


def extract_reviews() -> list[dict]:
    # TODO: duckdb.connect(str(WAREHOUSE), read_only=True) ושאילתת SQL שמחזירה רשימת dict-ים
    ...


def index(embedder) -> int:
    reviews = extract_reviews()
    # TODO: vectors = embedder([...טקסטים...])   (רמז: שם מוצר + טקסט הביקורת נותן הקשר טוב יותר)
    # TODO: records = [{**review, "vector": v.tolist()} ...]
    # TODO: lancedb.connect(...).create_table(TABLE, data=records, mode="overwrite")
    ...


def query(embedder, text: str, max_rating: int = 2, k: int = 5) -> list[dict]:
    table = lancedb.connect(str(DB_DIR)).open_table(TABLE)
    qvec = embedder([text])[0].tolist()
    # TODO: table.search(qvec) + סינון rating <= max_rating (רמז: .where(..., prefilter=True)) + limit(k)
    ...


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query")
    ap.add_argument("--fake-embeddings", action="store_true")
    args = ap.parse_args()
    embedder = rag.Embedder(fake=args.fake_embeddings)

    if args.query:
        for h in query(embedder, args.query):
            print(f"⭐{h['rating']} [{h['product_name']}] {h['review_text']}")
    else:
        print("indexed reviews:", index(embedder))


if __name__ == "__main__":
    main()

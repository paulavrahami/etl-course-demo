"""
תרגיל כיתה - שלב 4: מהמחסן ל-Vector DB, וחיפוש סמנטי עם סינון metadata   [פתרון]
הרצה:
    python pipelines/05_reviews_rag.py                       # אינדוקס
    python pipelines/05_reviews_rag.py --query "על מה לקוחות מתלוננים?"
"""
import argparse
import importlib.util
import json
from pathlib import Path

import duckdb
import lancedb
import pyarrow as pa

ROOT = Path(__file__).resolve().parent.parent
WAREHOUSE = ROOT / "warehouse.duckdb"
DB_DIR = ROOT / "lancedb"
TABLE = "reviews"

# שימוש חוזר ב-Embedder מהמודול של ה-RAG
_spec = importlib.util.spec_from_file_location("rag", ROOT / "pipelines" / "03_rag_pipeline.py")
rag = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rag)


def extract_reviews() -> list[dict]:
    """Extract: קוראים את הנתונים *הנקיים* מ-staging - לא מ-raw!"""
    with duckdb.connect(str(WAREHOUSE), read_only=True) as con:
        rows = con.sql("""
            select r.review_id, r.product_id, p.product_name, r.rating, r.review_text
            from staging.stg_reviews r
            join staging.stg_products p using (product_id)
        """).fetchall()
    cols = ["review_id", "product_id", "product_name", "rating", "review_text"]
    return [dict(zip(cols, r)) for r in rows]


def index(embedder) -> int:
    reviews = extract_reviews()
    vectors = embedder([f"{r['product_name']}: {r['review_text']}" for r in reviews])
    records = [{**r, "vector": v.tolist()} for r, v in zip(reviews, vectors)]
    schema = pa.schema([
        ("review_id", pa.int64()), ("product_id", pa.int64()),
        ("product_name", pa.string()), ("rating", pa.int64()),
        ("review_text", pa.string()), ("vector", pa.list_(pa.float32(), embedder.dimension)),
    ], metadata={"embedding_signature": json.dumps(embedder.signature, sort_keys=True)})
    # מכינים את כל הרשומות לפני overwrite; הסכמה מאפשרת גם תוצאה ריקה.
    lancedb.connect(str(DB_DIR)).create_table(TABLE, data=records or None,
                                            schema=schema, mode="overwrite")
    return len(records)


def query(embedder, text: str, max_rating: int = 2, k: int = 5) -> list[dict]:
    if not isinstance(max_rating, int) or not 1 <= max_rating <= 5 or k <= 0:
        raise ValueError("max_rating must be 1..5 and k must be positive")
    table = lancedb.connect(str(DB_DIR)).open_table(TABLE)
    saved = (table.schema.metadata or {}).get(b"embedding_signature")
    if saved is None or json.loads(saved) != embedder.signature:
        raise RuntimeError("Embedding mode/model differs from the reviews index. Run indexing again with the same mode.")
    qvec = embedder([text])[0].tolist()
    # סינון metadata לפני החיפוש: רק ביקורות שליליות
    return table.search(qvec).where(f"rating <= {max_rating}", prefilter=True).limit(k).to_list()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query")
    ap.add_argument("--fake-embeddings", action="store_true")
    args = ap.parse_args()
    if args.fake_embeddings:
        print("מצב הדגמה: hashing vectors בלבד; התוצאות אינן בדיקת איכות של חיפוש סמנטי.")
    embedder = rag.Embedder(fake=args.fake_embeddings)

    if args.query:
        for h in query(embedder, args.query):
            print(f"⭐{h['rating']} [{h['product_name']}] {h['review_text']}")
    else:
        print("indexed reviews:", index(embedder))


if __name__ == "__main__":
    main()

"""Check the environment and cache the real embedding model before class."""
import argparse
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CORE = ["pandas", "dlt", "duckdb", "dbt.version", "dagster", "dagster_dbt"]
RAG = ["pyarrow", "torch", "lancedb", "sentence_transformers"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-only", action="store_true", help="Check Python, dlt, dbt and Dagster only")
    parser.add_argument("--skip-model-download", action="store_true", help="Check imports only; does not verify RAG readiness")
    args = parser.parse_args()
    (ROOT / ".dagster_home").mkdir(exist_ok=True)
    ok = True
    for name in CORE + ([] if args.core_only else RAG):
        try:
            module = importlib.import_module(name)
            version = getattr(module, "__version__", getattr(module, "installed", ""))
            print(f"OK  {name:<24} {version}")
        except Exception as exc:
            ok = False
            print(f"FAIL {name:<24} {exc}")
    if not ok:
        print("\nההתקנה עדיין אינה מוכנה. יש לתקן את השגיאות ולהריץ שוב.")
        return 1
    if args.core_only:
        print("\nסביבת הליבה מוכנה. רכיבי RAG והמודל לא נבדקו במצב זה.")
        return 0
    if args.skip_model_download:
        print("\nהחבילות נטענו. המודל לא נבדק; להרצת RAG מלאה יש להריץ ללא --skip-model-download.")
        return 0
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(MODEL)
        vectors = model.encode(["בדיקת סביבת הלימוד"], normalize_embeddings=True)
        print(f"OK  embedding model: {MODEL}; dimension={vectors.shape[1]}")
    except Exception as exc:
        print(f"FAIL embedding model: {exc}")
        print("\nהמודל אינו מוכן. בדקו חיבור לרשת והריצו שוב לפני השיעור.")
        return 1
    print("\nהסביבה מוכנה, כולל embedding אמיתי. בדיקת ההדגמה: make preflight")
    return 0


if __name__ == "__main__":
    sys.exit(main())

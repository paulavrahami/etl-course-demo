"""
מודול 3 - ETL לנתונים לא-מובנים: Pipeline ל-RAG
=================================================
אותם עקרונות ETL, רק שהנתונים הם מסמכים והיעד הוא Vector DB:

  Extract   -> קריאת מסמכי Markdown מ-data/docs
  Transform -> ניקוי, חיתוך ל-chunks (לפי כותרות + גודל + חפיפה), יצירת embeddings
  Load      -> LanceDB (קובץ מקומי, בלי שרת)

עקרונות הנדסיים שרואים כאן:
  * אינקרמנטליות: hash לכל מסמך - מאנדקסים מחדש רק מה שהשתנה
  * אידמפוטנטיות: עדכון לפי chunk_id, ומחיקת chunks שהתיישנו באותה פעולת merge
  * Metadata: לכל chunk יש מקור וסעיף - בשביל ציטוט וסינון

הרצה:
    python pipelines/03_rag_pipeline.py                         # אינדוקס
    python pipelines/03_rag_pipeline.py --query "תוך כמה זמן אפשר להחזיר מוצר?"
    python pipelines/03_rag_pipeline.py --rebuild               # אינדוקס מאפס
    python pipelines/03_rag_pipeline.py --fake-embeddings ...   # בלי להוריד מודל (לבדיקות מהירות)

אופציונלי: מוסיפים --generate לשאילתה עם ANTHROPIC_API_KEY ו-CLAUDE_MODEL תקף כדי להפעיל Generation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import textwrap
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "data" / "docs"
DB_DIR = ROOT / "lancedb"
STATE_FILE = DB_DIR / "_index_state.json"
TABLE = "kb_chunks"

# מודל רב-לשוני (תומך עברית). ההורדה הראשונית היא כמה מאות MB.
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
FAKE_DIM = 256
CHUNKING_VERSION = "markdown-v2-400-1"


# ================================================================= EXTRACT
def extract_docs(folder: Path = DOCS) -> list[dict]:
    docs = []
    for path in sorted(folder.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        docs.append({"source": path.name, "text": text,
                     "doc_hash": hashlib.sha256(text.encode()).hexdigest()[:16]})
    return docs


# =============================================================== TRANSFORM
def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def chunk_markdown(doc: dict, max_chars: int = 400, overlap_sentences: int = 1) -> list[dict]:
    """
    אסטרטגיה: קודם לפי כותרות (##) כדי לשמור על משמעות, ואז לפי גודל עם חפיפה.
    max_chars מגביל את גוף ה-chunk, לפני כותרת ההקשר. יש להתאים גם למגבלת הטוקנים של המודל.
    כותרת ההקשר (שם המסמך + הסעיף) נותנת לקורא ולמודל את הקשר המקור.
    """
    if max_chars <= 0 or overlap_sentences < 0:
        raise ValueError("max_chars must be positive; overlap_sentences must be non-negative")
    text = clean_text(doc["text"])
    title_match = re.search(r"^#\s+(.+)$", text, re.M)
    title = title_match.group(1).strip() if title_match else doc["source"]
    # שומרים גם פתיח לפני ## וגם מסמך שאין בו כותרות.
    if title_match:
        text = (text[:title_match.start()] + text[title_match.end():]).strip()
    parts = re.split(r"^##\s+([^\n]+)\n?", text, flags=re.M)
    sections = [("כללי", parts[0])]
    sections += [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]
    chunks: list[dict] = []
    for heading, body in sections:
        # גם משפט בודד ארוך צריך להתחלק; חפיפה לא רשאית לפרוץ את התקציב.
        sentences = [piece for sentence in split_sentences(body)
                     for piece in textwrap.wrap(sentence, width=max_chars,
                                                break_long_words=True, break_on_hyphens=False)]

        current: list[str] = []
        for sent in sentences:
            if current and len(" ".join(current + [sent])) > max_chars:
                chunks.append(_make_chunk(doc, title, heading, current, len(chunks)))
                current = current[-overlap_sentences:] if overlap_sentences else []
                while current and len(" ".join(current + [sent])) > max_chars:
                    current.pop(0)
            current.append(sent)
        if current:
            chunks.append(_make_chunk(doc, title, heading, current, len(chunks)))
    return chunks


def _make_chunk(doc: dict, title: str, heading: str, sentences: list[str], idx: int) -> dict:
    body = " ".join(sentences)
    return {
        "chunk_id": f"{doc['source']}::{idx}",
        "source": doc["source"],
        "section": heading,
        "text": f"{title} > {heading}: {body}",
        "doc_hash": doc["doc_hash"],
    }


class Embedder:
    """עוטף את מודל ה-embeddings. fake=True -> וקטורי hashing (מהיר, בלי הורדה, איכות נמוכה)."""

    def __init__(self, fake: bool = False):
        self.fake = fake
        if not fake:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(EMBED_MODEL, device="cpu")
        self.dimension = FAKE_DIM if fake else (
            self.model.get_embedding_dimension() if hasattr(self.model, "get_embedding_dimension")
            else self.model.get_sentence_embedding_dimension())

    @property
    def signature(self) -> dict:
        return {"model": "hashing-demo-v1" if self.fake else EMBED_MODEL,
                "dimension": self.dimension, "normalize": True}

    def __call__(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)
        if self.fake:
            return np.stack([_hash_embed(t) for t in texts])
        return self.model.encode(texts, normalize_embeddings=True, batch_size=32)


def _hash_embed(text: str, dim: int = FAKE_DIM) -> np.ndarray:
    vec = np.zeros(dim, dtype=np.float32)
    words = re.findall(r"\w+", text.lower())
    for w in words + [a + b for a, b in zip(words, words[1:])]:
        vec[int(hashlib.md5(w.encode()).hexdigest(), 16) % dim] += 1.0
    n = np.linalg.norm(vec)
    return vec / n if n else vec


# ==================================================================== LOAD
def load_state() -> dict:
    return json.loads(STATE_FILE.read_text(encoding="utf-8")) if STATE_FILE.exists() else {}


def save_state(state: dict) -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    temp = STATE_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(STATE_FILE)


def index_signature(embedder: Embedder) -> dict:
    return {**embedder.signature, "chunking": CHUNKING_VERSION}


def sql_strings(values) -> str:
    """SQL literals for filenames, including names that contain an apostrophe."""
    return ", ".join("'" + value.replace("'", "''") + "'" for value in sorted(values))


def chunk_schema(dimension: int):
    import pyarrow as pa
    return pa.schema([(name, pa.string()) for name in
                      ["chunk_id", "source", "section", "text", "doc_hash"]]
                     + [("vector", pa.list_(pa.float32(), dimension))])


def index_documents(embedder: Embedder, rebuild: bool = False) -> dict:
    import lancedb

    db = lancedb.connect(str(DB_DIR))
    saved = load_state()
    names = db.list_tables().tables if hasattr(db, "list_tables") else db.table_names()
    table = db.open_table(TABLE) if TABLE in names else None
    # מודל אחר, מצב fake אחר או טבלה חסרה דורשים אינדוקס מחדש, גם אם המסמכים לא השתנו.
    rebuild = rebuild or table is None or saved.get("index") != index_signature(embedder)
    state = {} if rebuild else saved.get("documents", {})
    docs = extract_docs()

    changed = [d for d in docs if state.get(d["source"]) != d["doc_hash"]]
    removed = set(state) - {d["source"] for d in docs}
    stats = {"docs": len(docs), "changed": len(changed), "removed": len(removed), "chunks_written": 0}

    # מחשבים קודם את כל הווקטורים. כשל ב-embedding משאיר את האינדקס הישן זמין.
    records = []
    for doc in changed:
        chunks = chunk_markdown(doc)
        vectors = embedder([c["text"] for c in chunks])
        records += [{**c, "vector": v.tolist()} for c, v in zip(chunks, vectors)]

    if rebuild:
        # overwrite גם במקרה שאין מסמכים, כדי לא להשאיר נתונים ישנים אחרי --rebuild.
        db.create_table(TABLE, data=records or None, schema=chunk_schema(embedder.dimension),
                        mode="overwrite")
    elif records:
        affected = {d["source"] for d in changed} | removed
        (table.merge_insert("chunk_id")
         .when_matched_update_all()
         .when_not_matched_insert_all()
         .when_not_matched_by_source_delete(f"source IN ({sql_strings(affected)})")
         .execute(records))
    elif changed or removed:
        affected = {d["source"] for d in changed} | removed
        table.delete(f"source IN ({sql_strings(affected)})")
    stats["chunks_written"] = len(records)

    save_state({"index": index_signature(embedder),
                "documents": {d["source"]: d["doc_hash"] for d in docs}})
    return stats


# ================================================================== QUERY
def search(embedder: Embedder, query: str, k: int = 3) -> list[dict]:
    import lancedb
    if load_state().get("index") != index_signature(embedder):
        raise RuntimeError("Embedding mode/model differs from the index. Run indexing again with the same mode before querying.")
    table = lancedb.connect(str(DB_DIR)).open_table(TABLE)
    qvec = embedder([query])[0]
    return table.search(qvec.tolist()).limit(k).to_list()


def generate_answer(query: str, hits: list[dict]) -> str | None:
    """שלב ה-G ב-RAG. אופציונלי - דורש מפתח API ומזהה מודל מפורש."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        return None
    model_name = os.getenv("CLAUDE_MODEL")
    if not model_name:
        raise RuntimeError("Set CLAUDE_MODEL to a valid model ID before enabling generation.")
    import anthropic

    context = "\n\n".join(f"[{h['source']}] {h['text']}" for h in hits)
    msg = anthropic.Anthropic().messages.create(
        model=model_name,
        max_tokens=400,
        messages=[{"role": "user", "content":
                   f"ענה בעברית על סמך ההקשר בלבד, וציין את המקור.\n\nהקשר:\n{context}\n\nשאלה: {query}"}],
    )
    return msg.content[0].text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query")
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--fake-embeddings", action="store_true")
    ap.add_argument("--generate", action="store_true", help="Also call the optional LLM API; requires --query and configured credentials/model")
    args = ap.parse_args()
    if args.generate and not args.query:
        ap.error("--generate requires --query")
    if args.generate and not os.getenv("ANTHROPIC_API_KEY"):
        ap.error("--generate requires ANTHROPIC_API_KEY and CLAUDE_MODEL")

    if args.fake_embeddings:
        print("מצב הדגמה: hashing vectors בלבד; התוצאות אינן בדיקת איכות של חיפוש סמנטי.")
    embedder = Embedder(fake=args.fake_embeddings)
    if args.query:
        hits = search(embedder, args.query)
        for i, h in enumerate(hits, 1):
            print(f"{i}. [{h['source']} / {h['section']}] (distance={h['_distance']:.3f})\n   {h['text']}\n")
        if args.generate:
            if answer := generate_answer(args.query, hits):
                print("🤖 תשובה:\n" + answer)
    else:
        print("אינדוקס:", index_documents(embedder, rebuild=args.rebuild))


if __name__ == "__main__":
    main()

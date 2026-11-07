"""
מודול 1 - ETL "ידני" ב-Python טהור (pandas + SQLite)
=======================================================
המטרה: לראות את שלושת השלבים E-T-L בעיניים, בלי שום פריימוורק.
אחרי שמבינים את הכאב (קוד ידני, אין סכמה, אין אינקרמנטליות) - עוברים ל-dlt ו-dbt.

הרצה:  python pipelines/01_pure_python_etl.py
תוצר:  warehouse_basic.db (SQLite) עם הטבלאות customers, orders, daily_revenue
"""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DB_PATH = ROOT / "warehouse_basic.db"


# ----------------------------------------------------------------- EXTRACT
def extract() -> dict[str, pd.DataFrame]:
    """קוראים את הקבצים כמו שהם - הכל כטקסט, בלי לנחש טיפוסים."""
    return {
        "customers": pd.read_csv(RAW / "customers.csv", dtype=str),
        "orders": pd.read_csv(RAW / "orders.csv", dtype=str, keep_default_na=False),
        "products": pd.read_csv(RAW / "products.csv"),
    }


# --------------------------------------------------------------- TRANSFORM
def parse_mixed_dates(s: pd.Series) -> pd.Series:
    """תאריכים מגיעים גם כ-2026-03-01 וגם כ-01/03/2026."""
    iso = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")
    il = pd.to_datetime(s, format="%d/%m/%Y", errors="coerce")
    return iso.fillna(il).dt.date


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["email"] = df["email"].str.strip().str.lower()
    df["city"] = df["city"].str.strip().replace({"Tel Aviv": "תל אביב"})
    df["signup_date"] = parse_mixed_dates(df["signup_date"])
    df["customer_id"] = df["customer_id"].astype(int)
    # דה-דופליקציה: שומרים את הרשומה המעודכנת ביותר לכל לקוח
    df = df.sort_values("updated_at").drop_duplicates("customer_id", keep="last")
    return df.reset_index(drop=True)


def clean_orders(df: pd.DataFrame, valid_customers: set[int]) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df.copy()
    df["amount"] = pd.to_numeric(df["amount"].str.replace("₪", "", regex=False), errors="coerce")
    df["status"] = df["status"].str.strip().str.lower()
    df["order_date"] = parse_mixed_dates(df["order_date"])
    for c in ["order_id", "customer_id", "product_id", "quantity"]:
        df[c] = df[c].astype(int)

    # שורות פסולות לא נמחקות בשקט - שומרים אותן בטבלת "הסגר" (quarantine)
    bad = df["amount"].isna() | df["order_date"].isna() | ~df["customer_id"].isin(valid_customers)
    rejected = df[bad].assign(reject_reason="missing amount/date or unknown customer")
    return df[~bad].reset_index(drop=True), rejected.reset_index(drop=True)


def build_daily_revenue(orders: pd.DataFrame) -> pd.DataFrame:
    paid = orders[orders["status"] == "paid"]
    return (paid.groupby("order_date", as_index=False)
                .agg(orders=("order_id", "count"), revenue=("amount", "sum"))
                .sort_values("order_date"))


# -------------------------------------------------------------------- LOAD
def load(tables: dict[str, pd.DataFrame]) -> None:
    """Full refresh: מוחקים ויוצרים מחדש. פשוט, אבל לא מתאים לנתונים גדולים."""
    with sqlite3.connect(DB_PATH) as con:
        for name, df in tables.items():
            df.to_sql(name, con, if_exists="replace", index=False)


def main() -> None:
    raw = extract()
    customers = clean_customers(raw["customers"])
    orders, rejected = clean_orders(raw["orders"], set(customers["customer_id"]))
    daily = build_daily_revenue(orders)

    load({"customers": customers, "orders": orders, "orders_rejected": rejected,
          "products": raw["products"], "daily_revenue": daily})

    print(f"E: customers={len(raw['customers'])} orders={len(raw['orders'])}")
    print(f"T: customers אחרי ניקוי={len(customers)} | orders תקינות={len(orders)} | נדחו={len(rejected)}")
    print(f"L: נטען ל-{DB_PATH.name} | הכנסות (paid) = ₪{daily['revenue'].sum():,.2f}")


if __name__ == "__main__":
    main()

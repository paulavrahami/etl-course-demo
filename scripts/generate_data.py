"""
מחולל נתונים לקורס - יוצר נתונים "מלוכלכים" בכוונה לחנות מקוונת דמיונית "ShopIL".

הרצה:  python scripts/generate_data.py
התוצר נכתב ל-data/raw/

הלכלוך המכוון (בשביל ללמד ניקוי):
  - לקוחות כפולים (אותו מייל, אותיות גדולות/רווחים)
  - סכומים כטקסט: "120.50", "₪89.90", "N/A", ריק
  - תאריכים בשני פורמטים: 2026-03-01 וגם 01/03/2026
  - סטטוסים לא עקביים: "Paid", "paid ", "PAID"
  - ביקורות עם דירוג לא חוקי (0, 7), ביקורות כפולות, טקסט ריק
"""
import csv
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

random.seed(42)
OUT = Path(__file__).resolve().parent.parent / "data" / "raw"
OUT.mkdir(parents=True, exist_ok=True)

FIRST = ["נועה", "איתי", "מאיה", "יונתן", "תמר", "אורי", "שירה", "דניאל", "רוני", "עומר",
         "Lior", "Dana", "Amit", "Yael", "Noam"]
LAST = ["כהן", "לוי", "מזרחי", "פרץ", "ביטון", "אברהם", "פרידמן", "Shapiro", "Katz", "Golan"]
CITIES = ["תל אביב", "ירושלים", "חיפה", "באר שבע", "רמת גן", "Tel Aviv", "  חיפה ", "ראשון לציון"]

PRODUCTS = [
    (1, "אוזניות אלחוטיות", "אלקטרוניקה", 349.0),
    (2, "מקלדת מכנית", "אלקטרוניקה", 459.0),
    (3, "בקבוק מים תרמי", "בית", 89.9),
    (4, "תיק גב למחשב", "אביזרים", 229.0),
    (5, "מטען מהיר USB-C", "אלקטרוניקה", 119.0),
    (6, "ספל קרמיקה", "בית", 49.9),
    (7, "עכבר ארגונומי", "אלקטרוניקה", 199.0),
    (8, "מעמד לטלפון", "אביזרים", 59.0),
]

START = date(2026, 1, 1)


def fmt_date(d: date) -> str:
    # 25% מהתאריכים בפורמט ישראלי
    return d.strftime("%d/%m/%Y") if random.random() < 0.25 else d.isoformat()


def messy_amount(v: float) -> str:
    r = random.random()
    if r < 0.04:
        return "N/A"
    if r < 0.07:
        return ""
    if r < 0.25:
        return f"₪{v:.2f}"
    return f"{v:.2f}"


def main() -> None:
    # ---------- customers ----------
    customers = []
    for cid in range(1, 121):
        fn, ln = random.choice(FIRST), random.choice(LAST)
        email = f"user{cid}@example.com"
        customers.append({
            "customer_id": cid,
            "full_name": f"{fn} {ln}",
            "email": email,
            "city": random.choice(CITIES),
            "signup_date": fmt_date(START + timedelta(days=random.randint(0, 200))),
            "updated_at": datetime(2026, 7, 1, 10, 0).isoformat(),
        })
    # כפילויות: אותו לקוח שוב עם מייל באותיות גדולות ועדכון מאוחר יותר
    for c in random.sample(customers, 8):
        dup = dict(c)
        dup["email"] = "  " + c["email"].upper()
        dup["updated_at"] = datetime(2026, 8, 15, 12, 0).isoformat()
        customers.append(dup)
    random.shuffle(customers)

    with open(OUT / "customers.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(customers[0].keys()))
        w.writeheader()
        w.writerows(customers)

    # ---------- products ----------
    with open(OUT / "products.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["product_id", "product_name", "category", "list_price"])
        w.writerows(PRODUCTS)

    # ---------- orders ----------
    statuses = ["paid", "Paid", "PAID ", "refunded", "pending", "cancelled"]
    orders = []
    for oid in range(1001, 1601):
        p = random.choice(PRODUCTS)
        qty = random.choices([1, 2, 3], weights=[75, 20, 5])[0]
        d = START + timedelta(days=random.randint(0, 270))
        orders.append({
            "order_id": oid,
            "customer_id": random.randint(1, 125),  # חלק מהלקוחות לא קיימים! (orphan)
            "product_id": p[0],
            "quantity": qty,
            "amount": messy_amount(p[3] * qty),
            "status": random.choices(statuses, weights=[40, 20, 10, 8, 12, 10])[0],
            "order_date": fmt_date(d),
            "updated_at": datetime.combine(d, datetime.min.time()).replace(hour=random.randint(8, 22)).isoformat(),
        })
    with open(OUT / "orders.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(orders[0].keys()))
        w.writeheader()
        w.writerows(orders)

    # ---------- reviews (לתרגיל בכיתה) ----------
    good = ["מוצר מעולה, הגיע מהר", "איכות גבוהה ממה שציפיתי", "שווה כל שקל", "Great product, works perfectly",
            "קל לשימוש ונראה טוב", "השירות היה מצוין"]
    bad = ["המשלוח לקח שלושה שבועות", "הגיע שבור באריזה", "הסוללה מחזיקה רק שעתיים", "לא תואם לתיאור באתר",
           "שירות הלקוחות לא ענה למיילים", "Stopped working after a week", "המחיר גבוה מדי ביחס לאיכות",
           "האריזה הייתה פתוחה כשהגיע"]
    reviews = []
    for rid in range(1, 301):
        rating = random.choices([1, 2, 3, 4, 5], weights=[10, 10, 15, 30, 35])[0]
        text = random.choice(bad if rating <= 2 else good if rating >= 4 else good + bad)
        reviews.append({
            "review_id": rid,
            "order_id": random.randint(1001, 1600),
            "product": {"id": random.choice(PRODUCTS)[0]},  # מבנה מקונן בכוונה
            "rating": rating,
            "text": text,
            "created_at": (datetime(2026, 2, 1) + timedelta(hours=random.randint(0, 6000))).isoformat(),
            "tags": random.sample(["משלוח", "איכות", "מחיר", "שירות", "אריזה"], k=random.randint(0, 2)),
        })
    # לכלוך: דירוגים לא חוקיים, טקסט ריק, כפילויות
    for r in random.sample(reviews, 6):
        r["rating"] = random.choice([0, 7, None])
    for r in random.sample(reviews, 5):
        r["text"] = "   "
    reviews.extend(dict(r) for r in random.sample(reviews, 10))

    with open(OUT / "reviews.json", "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=1)

    # ---------- sample GitHub issues (גיבוי אופליין למקור ה-API) ----------
    issues = []
    for i in range(1, 41):
        issues.append({
            "id": 900000 + i,
            "number": i,
            "title": f"Sample issue #{i}",
            "state": random.choice(["open", "closed"]),
            "user": {"login": random.choice(["alice", "bob", "carol"]), "id": random.randint(1, 99)},
            "labels": [{"name": n} for n in random.sample(["bug", "enhancement", "docs", "question"], k=random.randint(0, 2))],
            "comments": random.randint(0, 12),
            "created_at": (datetime(2026, 1, 1) + timedelta(days=i * 3)).isoformat() + "Z",
            "updated_at": (datetime(2026, 1, 5) + timedelta(days=i * 3)).isoformat() + "Z",
        })
    with open(OUT / "github_issues_sample.json", "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=1)

    print(f"✅ נוצרו קבצים ב-{OUT}: customers={len(customers)} orders={len(orders)} "
          f"reviews={len(reviews)} products={len(PRODUCTS)} issues={len(issues)}")


if __name__ == "__main__":
    main()

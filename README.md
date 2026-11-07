# ETL for AI Engineering: סביבת הדגמה

[מאגר הקורס](https://github.com/paulavrahami/etl-course-demo) | [פתיחת סביבת תרגול ב GitHub Codespaces](https://codespaces.new/paulavrahami/etl-course-demo)

סביבת הדגמה לקורס. עיבוד הנתונים והחיפוש רצים מקומית; התקנת החבילות והורדת מודל ה־embeddings דורשות רשת בפעם הראשונה. אפשר לעבוד גם ב־GitHub Codespaces עם חשבון GitHub.
החנות הדמיונית **ShopIL** מייצרת נתונים מלוכלכים בכוונה (כפילויות, תאריכים בשני פורמטים, סכומים כטקסט ו-JSON מקונן), ומסמכי ידע בעברית ל-RAG.

**להתחלה ב־Windows עם Cursor ו־uv:** פותחים את [`WINDOWS_UV_START.md`](WINDOWS_UV_START.md). המחברת [`ETL_Course_Lab_HE.ipynb`](ETL_Course_Lab_HE.ipynb) כבר כלולה במאגר, לצד קובצי הפרויקט.

**לסטודנטים:** מדריך ההתחלה הוא [`STUDENT_QUICKSTART.md`](STUDENT_QUICKSTART.md). **למרצה:** מדריך ההדגמה ב־[`INSTRUCTOR_GUIDE.md`](INSTRUCTOR_GUIDE.md); מצב הרצת הניסיון ב־[`TRIAL_REPORT.md`](TRIAL_REPORT.md).

```
 מקורות                 E/L              אחסון (DuckDB)                    T                    צריכה
┌──────────────┐                 ┌───────────────────────────────┐
│ CSV  (orders)│──┐              │ raw      staging      marts   │
│ JSON (reviews│──┼──► dlt ────► │ ─────►  ───────►   ─────────  │──► BI / Features ל-ML
│ REST (GitHub)│──┘              │          dbt models + tests   │
└──────────────┘                 └───────────────────────────────┘
┌──────────────┐   chunk → embed                 ┌────────────┐
│ Markdown docs│ ─────────────────────────────►  │  LanceDB   │──► RAG / חיפוש סמנטי ──► LLM
└──────────────┘                                 └────────────┘
                 Dagster: מתזמן, מנטר ומציג lineage של כל הנכסים
```

## התקנה

### אפשרות א: Windows, Cursor ו־uv עם Python 3.13.12

פותחים ב־Cursor את תיקיית הפרויקט. אם מתחילים בעותק חדש, משכפלים לתיקייה פנויה; אם כבר יש עותק מעודכן במחשב, משתמשים בו. ההוראות המלאות להורדה ולעדכון נמצאות ב־[`WINDOWS_UV_START.md`](WINDOWS_UV_START.md).

בטרמינל שבשורש הפרויקט, **רק אם עדיין אין סביבה לפרויקט**, יוצרים אותה:

```powershell
uv venv --python 3.13.12
```

מתקינים את החבילות באותה סביבה:

```powershell
uv pip install --python .venv\Scripts\python.exe torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu
uv pip install --python .venv\Scripts\python.exe -r requirements-notebook.txt
```

פותחים את `ETL_Course_Lab_HE.ipynb`, לוחצים **Select Kernel**, בוחרים **Python Environments** ואת `.venv\Scripts\python.exe`, ומריצים תא אחר תא באמצעות **Shift+Enter**. המחברת מציגה נתוני מקור, תוצאות ובדיקות בכל שלב, ושומרת את תוצרי ההרצה בתיקייה נפרדת בתוך `notebook_lab`. הוראות המחברת משתמשות ישירות ב־uv להתקנת החבילות.

המחברת כוללת גם פתרון מלא למרצה בחלק הביקורות. סטודנטים שמבצעים את התרגיל בעצמם עוצרים לפני חלק הפתרון. סביבת Codespaces ומסלולי הטרמינל הקיימים של Python 3.11 ו־3.12 נשארים זמינים בהמשך.

### אפשרות ב: GitHub Codespaces

1. פותחים את [מאגר הקורס](https://github.com/paulavrahami/etl-course-demo) ונכנסים לחשבון GitHub האישי.
2. לוחצים **Code → Codespaces → Create codespace on main**.
3. ממתינים לסיום ההתקנה האוטומטית. הסביבה מתקינה חבילות, מייצרת נתונים ומורידה מודל embeddings. הזמן תלוי ברשת ובמחשב; מבצעים זאת לפני השיעור.
4. מריצים `make preflight`. ההודעה הסופית מאשרת את הרצת ההדגמה; עדיין בודקים שהחיפוש החזיר מקורות רלוונטיים.

אפשר להגיע ישירות לעמוד יצירת הסביבה דרך [קישור הפתיחה](https://codespaces.new/paulavrahami/etl-course-demo). כל סטודנט או זוג יוצר סביבת עבודה משלו.

### אפשרות ג: התקנה מקומית דרך הטרמינל עם Python 3.11 או 3.12

מורידים את הקוד באמצעות **Code > Download ZIP** ומחלצים אותו, או משכפלים באמצעות Git:

```bash
git clone https://github.com/paulavrahami/etl-course-demo.git
cd etl-course-demo
```

מתוך תיקיית הפרויקט:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python scripts/setup_classroom.py
python scripts/preflight.py
```
> ב-Windows אין `make`, אז מריצים את הפקודות שמופיעות ב-Makefile ישירות.

סקריפט ההתקנה מתקין תחילה torch מ־CPU index ב־Linux/Windows. אין הבטחה להתקנת CPU בלבד באמצעות `--extra-index-url`; לכן אין צורך להוסיף אותו ידנית. משקלי המודל הם בסדר גודל של מאות MB, בנוסף לחבילות Python, ויש להורידם מראש.

להתקנת החלק המובנה בלבד: `python scripts/setup_classroom.py --core-only`, ואחר כך `python scripts/preflight.py --core-only`. מסלול זה אינו בודק RAG.

## ההדגמה לפי מודולים

| # | נושא | פקודה | מה לראות |
|---|------|-------|----------|
| 1 | ETL ידני ב-Python | `make basic` | E-T-L בעיניים, טבלת quarantine לשורות פסולות |
| 2 | Extract & Load עם dlt | `make dlt` | schema inference, טעינה אינקרמנטלית (להריץ פעמיים!), טבלאות-בת מ-JSON |
| 3 | Transform עם dbt | `make dbt` | שכבות raw→staging→marts, בדיקות איכות, `dbt docs generate && dbt docs serve` |
| 4 | Pipeline ל-RAG | `make rag` ואז `make ask` | chunking, embeddings, אינדוקס אינקרמנטלי (לשנות מסמך ולהריץ שוב) |
| 5 | אורקסטרציה | `make dagster` → http://localhost:3000 | גרף נכסים, Materialize, בדיקות dbt כ-asset checks, schedule |

הכל ברצף: `make demo`. מתחילים מאפס: `make clean`.

**טיפים להדגמה חיה**

- **אינקרמנטליות:** מריצים `make dlt` פעמיים. בפעם השנייה ב-orders נטענות 0 שורות.
- **Schema evolution:** מוסיפים עמודה חדשה ל-`orders.csv`, ומעדכנים `updated_at` של רשומה אחת לערך מאוחר מנקודת ההמשך שכבר נשמרה. מריצים `make dlt` ומציגים את העמודה החדשה. הוספת עמודה ללא שינוי ה־cursor לא תעביר מחדש רשומות שסוננו. לפני חזרה לנתוני הבסיס מריצים `make clean` ואז `make data`.
- **בדיקה שנכשלת:** מוחקים את ה-`qualify` מ-`stg_customers.sql` ומריצים `make dbt`. בדיקת ה-unique נכשלת.
- **RAG אינקרמנטלי:** משנים משפט ב-`data/docs/shipping.md` ומריצים `make rag`. רק מסמך אחד מאונדקס מחדש.
- **Generation (הרחבה):** מגדירים `ANTHROPIC_API_KEY` ו־`CLAUDE_MODEL` למזהה מודל תקף בחשבון, ומריצים את שאילתת `03_rag_pipeline.py` עם `--generate`. רק הדגל הזה מפעיל את ה־API; `make ask` מבצע חיפוש מקומי בלבד. שלב זה לא נכלל בהרצת הניסיון ללא מפתח.
- **API אמיתי:** `python pipelines/02_dlt_pipeline.py` (בלי `--offline`). בכיתה כדאי להגדיר `GITHUB_TOKEN`, אחרת המגבלה היא 60 קריאות לשעה לכל כתובת IP.

## תרגיל הכיתה

ראו [`exercises/EXERCISE.md`](exercises/EXERCISE.md). מתחילים עם `make exercise-start` ובודקים עם `make check`.

## מבנה התיקייה

```
ETL_Course_Lab_HE.ipynb  מחברת הרצה, בדיקות ותוצאות
WINDOWS_UV_START.md      התחלה ב-Windows עם Cursor ו-uv
requirements-notebook.txt חבילות הפרויקט והתוספות למחברת
data/raw/            נתוני מקור (נוצרים ע"י scripts/generate_data.py)
data/docs/           מסמכי ידע ל-RAG
pipelines/           01 Python טהור | 02 dlt | 03 RAG | 04-05 תרגיל
dbt_project/         מודלים, בדיקות, profiles.yml (DuckDB)
orchestration/       Dagster definitions
exercises/           הוראות, starter, פתרון, בודק אוטומטי
INSTRUCTOR_GUIDE.md  מדריך מרצה: הרצת ניסיון ופלטים צפויים
```

## תקלות נפוצות

| תקלה | פתרון |
|------|-------|
| `IO Error: Could not set lock on file warehouse.duckdb` | יש תהליך אחר שמחזיק את הקובץ (DBeaver, notebook או Dagster). סוגרים אותו ומריצים שוב. |
| dbt: `Catalog "raw" does not exist` / `Table raw.orders does not exist` | צריך להריץ קודם את `make dlt`. |
| GitHub `403 rate limit` | מריצים עם `--offline` או מגדירים `GITHUB_TOKEN`. |
| הורדת המודל איטית בכיתה | מריצים `scripts/warmup.py` מראש. `--fake-embeddings` מאפשר בדיקת זרימת נתונים בלבד, ואינו חיפוש סמנטי. |
| מעבר בין וקטורים מדומים למודל אמיתי | מאנדקסים שוב עם אותו מצב שבו תבוצע השאילתה; הקוד מזהה שינוי במודל ובממד. |

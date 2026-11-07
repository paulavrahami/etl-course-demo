# התחלה לסטודנטים — ETL להנדסת AI

[מאגר הקורס](https://github.com/paulavrahami/etl-course-demo) | [פתיחת סביבת תרגול](https://codespaces.new/paulavrahami/etl-course-demo)

כל זוג צריך מחשב אחד, דפדפן וגישה לתיקיית הקורס. את ההתקנה ואת הורדת המודל מסיימים **לפני השיעור**. בזמן התרגיל עובדים על נתוני ShopIL המקומיים.

## מסלול א: GitHub Codespaces

1. פותחים את [מאגר הקורס](https://github.com/paulavrahami/etl-course-demo) ונכנסים לחשבון GitHub.
2. בוחרים **Code → Codespaces → Create codespace on main**. כל זוג עובד בסביבה משלו.
3. מחכים לסיום `postCreateCommand`. הפקודה מתקינה את החבילות, יוצרת את נתוני הדוגמה ומורידה את מודל ה־embeddings. הזמן תלוי ברשת ובמחשב; לא סוגרים את הסביבה באמצע.
4. בטרמינל בתיקיית הפרויקט מריצים:

```bash
python scripts/warmup.py
make preflight
```

הבדיקה צריכה להסתיים בהודעת הצלחה. אזהרת dbt על הזמנות שמפנות ללקוחות חסרים היא חלק מכוון מנתוני התרגול. שגיאת `ERROR` או קוד יציאה שאינו אפס דורשים תיקון לפני השיעור.

אם הגדרת המאגר או החשבון אינה מאפשרת לפתוח Codespace, משתמשים במסלול ההתקנה המקומית שבהמשך.

## מסלול ב: התקנה מקומית

נדרש Python 3.11 או 3.12; סביבת Codespaces המצורפת משתמשת ב־3.12. פותחים טרמינל בתיקייה שבה נמצאים `README.md` ו־`Makefile`.

להורדת הקוד בוחרים במאגר **Code > Download ZIP** ומחלצים את התיקייה. אם Git מותקן, אפשר לשכפל כך:

```bash
git clone https://github.com/paulavrahami/etl-course-demo.git
cd etl-course-demo
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python scripts/setup_classroom.py
python scripts/preflight.py
```

**Windows, ב־Command Prompt:**

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
python scripts/setup_classroom.py
python scripts/preflight.py
```

ב־Windows אפשר לעבוד בלי `make`: הפקודות המלאות מופיעות בהמשך וב־`Makefile`. אין צורך בחשבון ענן או במפתח API כדי להריץ את הדגמת הנתונים ואת החיפוש המקומי. יצירת תשובה באמצעות ספק LLM חיצוני היא הרחבה נפרדת.

## בדיקת תחילת שיעור

```bash
python pipelines/01_pure_python_etl.py
python pipelines/02_dlt_pipeline.py --offline
cd dbt_project
dbt build --profiles-dir .
cd ..
```

בנתוני הדוגמה המקוריים: 120 לקוחות נקיים, 549 הזמנות תקינות, 51 הזמנות בהסגר והכנסות מהזמנות `paid` בסך 97,210.10 ש״ח. בהרצה חוזרת של dlt מספר ההזמנות בטבלת raw נשאר 600, ולא נטענות הזמנות חדשות כשקובץ המקור לא השתנה.

להפעלת ממשק Dagster:

```bash
python scripts/start_dagster.py
```

פותחים את פורט 3000 מתוך לשונית **Ports** ב־Codespaces, או את `http://localhost:3000` במחשב המקומי. מסיימים את התהליך לפני פתיחת אותו קובץ DuckDB בכלי נוסף שעלול לנעול אותו.

## התחלת התרגיל

אחרי שההדגמה עובדת, מריצים **פעם אחת**:

```bash
make exercise-start
```

הפקודה מעתיקה את קובצי ההתחלה לתיקיות העבודה. הרצה חוזרת מחליפה את הפתרונות שכתבתם באותם קבצים, ולכן לא מריצים אותה שוב באמצע התרגיל.

ב־Windows ללא `make`, מעתיקים את הקבצים מתוך `exercises/starter` כך:

| קובץ | תיקיית יעד |
|---|---|
| `04_reviews_pipeline.py`, `05_reviews_rag.py` | `pipelines/` |
| `stg_reviews.sql` | `dbt_project/models/staging/` |
| `mart_product_reviews.sql`, `_reviews.yml` | `dbt_project/models/marts/` |

עובדים לפי `exercises/EXERCISE.md` ומשלימים את ה־TODO. לאחר כל שלב מריצים את הבודק של אותו שלב:

```bash
python exercises/check_exercise.py 1
python exercises/check_exercise.py 2
python exercises/check_exercise.py 3
python exercises/check_exercise.py 4
```

התוצרים הצפויים לנתוני הקורס: 310 ביקורות ב־raw, 289 ביקורות נקיות, 8 מוצרים ב־mart ו־289 רשומות באינדקס הביקורות. ביקורת שלילית מוגדרת בתרגיל כדירוג 2 ומטה.

## אם ההתקנה המלאה לא הסתיימה

אפשר להשלים את חלק הנתונים המובנים בנפרד:

```bash
python scripts/setup_classroom.py --core-only
python scripts/preflight.py --core-only
```

מסלול זה אינו מתקין או מאמת את RAG. להשלמת הקורס חוזרים בהמשך להתקנה המלאה ול־`warmup.py` ללא הדגל.

`--fake-embeddings` מיועד לבדיקת זרימת הנתונים בלבד. וקטורים מדומים אינם חיפוש סמנטי, ואין להעריך לפיהם את איכות התשובות.

## תקלות שכיחות

| מה רואים | הפעולה הבאה |
|---|---|
| חבילה חסרה או `dbt` לא נמצא | בודקים שהסביבה `.venv` פעילה ומריצים שוב את ההתקנה |
| הורדת מודל נכשלה | בודקים רשת ומריצים `python scripts/warmup.py` לפני השיעור |
| טבלת `raw.orders` חסרה | מריצים תחילה `python pipelines/02_dlt_pipeline.py --offline` |
| DuckDB מדווח על נעילה | סוגרים תהליך אחר שמחזיק את `warehouse.duckdb` ומנסים שוב |
| בדיקת תרגיל נכשלת | קוראים את הרמז ומריצים את מספר השלב בלבד |

למרצה: הבדיקה המלאה של הפתרון היא `make exercise-solution`. היא מעתיקה את קובצי הפתרון, ולכן אינה פקודת פתיחה לסטודנטים.

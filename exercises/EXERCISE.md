# תרגיל כיתה: ביקורות לקוחות, מ-JSON מלוכלך ל-RAG

**משך:** 90 דקות · **עבודה בזוגות** · **דרישה מוקדמת:** ההדגמה (`make demo`) רצה אצלכם בהצלחה

חלוקת הזמן: 5 דקות לתדריך, 80 דקות לארבעת השלבים ו־5 דקות להצגת התוצרים. ביקורת שלילית בתרגיל היא דירוג 2 ומטה. לפני שלב ה־mart מגדירים מה מייצגת שורה אחת; מאגדים ביקורות ומכירות בנפרד לפני שמחברים ביניהן.

## התרחיש
צוות המוצר ב-ShopIL קיבל ייצוא של ביקורות לקוחות (`data/raw/reviews.json`). הם צריכים:
1. דשבורד של דירוג ממוצע מול הכנסות לכל מוצר.
2. כלי שעונה על השאלה "על מה לקוחות מתלוננים?".

הנתונים מלוכלכים: יש ביקורות כפולות, דירוגים לא חוקיים (0, 7, null), טקסטים ריקים ומבנה מקונן (`product.id`, `tags[]`).

## התחלה
```bash
make exercise-start        # מעתיק את קבצי ה-starter למקומם
```
בכל קובץ יש הערות `TODO` במקומות שצריך להשלים.
מריצים את פקודת ההתחלה פעם אחת בלבד: הרצה חוזרת מחליפה את קובצי העבודה. לאחר תחילת התרגיל בודקים כל שלב בנפרד.

---

### שלב 1 · Extract & Load (15 דק')
**קובץ:** `pipelines/04_reviews_pipeline.py`
טענו את הביקורות ל-`raw.reviews` עם dlt.
```bash
python pipelines/04_reviews_pipeline.py
python exercises/check_exercise.py 1
```
❓ **שאלה לדיון:** אילו טבלאות נוצרו? למה dlt יצר את `reviews__tags`?

### שלב 2 · Transform (25 דק')
**קבצים:** `dbt_project/models/staging/stg_reviews.sql`, `dbt_project/models/marts/_reviews.yml`
נקו את הנתונים לפי הכללים העסקיים, והוסיפו בדיקות dbt.
```bash
cd dbt_project && dbt build --select stg_reviews --profiles-dir . && cd ..
python exercises/check_exercise.py 2
```
❓ **שאלה לדיון:** למה לא ניקינו כבר בשלב ה-Load?

### שלב 3 · Mart (20 דק')
**קובץ:** `dbt_project/models/marts/mart_product_reviews.sql`
בנו שורה לכל מוצר עם דירוג ממוצע, מספר ביקורות שליליות והכנסות.
```bash
cd dbt_project && dbt build --select +mart_product_reviews --profiles-dir . && cd ..
python exercises/check_exercise.py 3
```
❓ **שאלה לדיון:** איזה מוצר מכניס הרבה אבל מקבל דירוג נמוך? מה הייתם ממליצים לצוות?

### שלב 4 · AI (20 דק')
**קובץ:** `pipelines/05_reviews_rag.py`
טענו את הביקורות הנקיות ל-LanceDB, וחפשו תלונות רק בביקורות עם דירוג 2 ומטה.
```bash
python pipelines/05_reviews_rag.py
python pipelines/05_reviews_rag.py --query "על מה לקוחות מתלוננים?"
python exercises/check_exercise.py 4
```
❓ **שאלה לדיון:** מה היה קורה אם היינו מאנדקסים מ-`raw` במקום מ-`staging`?

---

## 🏆 בונוס (למי שסיים)
1. **Dagster:** הוסיפו את שלב 1 ושלב 4 כ-assets ב-`orchestration/definitions.py`. שימו לב שהתלות ב-dbt צריכה להופיע בגרף.
2. **Sensor:** כתבו sensor ב-Dagster שמריץ את `kb_vector_index` כשקובץ חדש נוסף ל-`data/docs/`.
3. **בדיקה עסקית:** כתבו בדיקה סינגולרית ב-dbt שנכשלת כשיותר מ-30% מהביקורות של מוצר שליליות.
4. **Generation:** חברו את תוצאות החיפוש ל-LLM (ראו `generate_answer` ב-`03_rag_pipeline.py`) וקבלו סיכום תלונות לכל מוצר.

## סיום
`make check` צריך להציג `🎉 N/N בדיקות עברו`.

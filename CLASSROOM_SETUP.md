# הכנת הכיתה — מדריך קצר למרצה

בכיתה שעובדת עם Windows, Cursor ו־uv מתחילים במסלול המחברת המקומית עם Python 3.13.12. חלופת הדפדפן היא GitHub Codespaces, עם סביבת Python 3.12 אישית לכל סטודנט או זוג. התרגול הבסיסי והחיפוש הסמנטי משתמשים בנתוני הדוגמה ובמודל מקומי; יצירת תשובה דרך ספק LLM היא הרחבה נפרדת.

## 1. מאגר הקורס

מאגר הקורס הציבורי: [paulavrahami/etl-course-demo](https://github.com/paulavrahami/etl-course-demo).

פתיחת סביבת תרגול: [GitHub Codespaces](https://codespaces.new/paulavrahami/etl-course-demo).

קובצי הפרויקט נמצאים בשורש המאגר. המחברת `ETL_Course_Lab_HE.ipynb`, מדריך Windows בשם `WINDOWS_UV_START.md` וקובץ `requirements-notebook.txt` כלולים בו, יחד עם `README.md`, `Makefile`, `requirements.txt`, התיקיות `scripts`, `pipelines`, `dbt_project` ו־`exercises`. הגדרת `.devcontainer/devcontainer.json` מפעילה התקנה אוטומטית כאשר יוצרים Codespace.

משקלי המודל והסביבה הווירטואלית מותקנים בעת ההקמה. המאגר כולל את קובצי ההתחלה ואת פתרון התרגיל במלואו, לצורך הדגמה ובדיקה עצמית.

## 2. הרצת ניסיון בסביבה חדשה

### Windows, Cursor ו־uv

מתחילים ב־[`WINDOWS_UV_START.md`](WINDOWS_UV_START.md). פותחים את הפרויקט ב־Cursor. אם מתחילים בעותק חדש, משכפלים לתיקייה פנויה ומשאירים את העותק הקודם ואת עבודת הסטודנטים במקומם.

רק כשאין עדיין סביבת עבודה לפרויקט:

```powershell
uv venv --python 3.13.12
```

בטרמינל שבשורש הפרויקט:

```powershell
uv pip install --python .venv\Scripts\python.exe torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu
uv pip install --python .venv\Scripts\python.exe -r requirements-notebook.txt
```

פותחים את `ETL_Course_Lab_HE.ipynb`, בוחרים **Select Kernel**, **Python Environments** ואת `.venv\Scripts\python.exe`. מריצים תא אחר תא באמצעות **Shift+Enter**. למרצה: משלימים גם את חלק פתרון הביקורות ואת הבודק בסוף המחברת, ובודקים שהחיפוש מחזיר מקורות רלוונטיים.

המחברת יוצרת עותק עבודה נפרד בתוך `notebook_lab` ומייצאת את הטבלאות ואת `results.html` לתיקיית `exports` של ההרצה. היא מציגה בנפרד את הפקודה לפתיחת Dagster; את ממשק הדפדפן ואת ההרצה ממנו יש לבדוק במחשב שבו מציגים.

### GitHub Codespaces

במאגר: **Code → Codespaces → Create codespace on main**. אם ענף ברירת המחדל נקרא אחרת, בחרו אותו. המתינו לסיום ההתקנה האוטומטית. ההקמה מורידה חבילות ואת מודל ה־embeddings, ולכן כדאי לבצע אותה לפני השיעור ולא בזמן הכניסה לכיתה.

בטרמינל שבשורש הפרויקט:

```bash
python scripts/preflight.py
make exercise-solution
python scripts/start_dagster.py
```

- `preflight.py` מריץ את ההדגמה, משווה תוצאות Python ו־dbt, טוען פעמיים לבדיקת התנהגות חוזרת, בודק את הגדרות Dagster ומבצע חיפוש עם המודל האמיתי. יש לבדוק גם את רלוונטיות תוצאות החיפוש המוצגות.
- `make exercise-solution` מיועד למרצה: הוא מעתיק את קובצי הפתרון ומריץ את פתרון התרגיל ואת הבודק. התוצאות הצפויות הן 310 ביקורות מקור, 289 ביקורות נקיות, 8 מוצרים ו־289 וקטורים.
- ב־Dagster פותחים את פורט 3000 מלשונית **Ports**, בודקים את גרף הנכסים ומפעילים הרצה. בקוד ההתחלתי מסלול ביקורות התרגיל אינו חלק מהגרף; הוספתו היא משימת הרחבה.

אזהרת dbt על הזמנות המקושרות ללקוחות חסרים היא חלק מכוון מנתוני הדוגמה. שגיאת `ERROR`, חריגה או קוד יציאה שאינו אפס דורשים טיפול. בדוח `TRIAL_REPORT.md` מתועדים מה הורץ בפועל, הגרסאות והתוצאות; בדיקת Codespaces במאגר הקורס שלכם היא בדיקה נוספת של סביבת ההפצה.

## 3. מה לשלוח לסטודנטים

לכיתה המקומית שולחים את [מאגר הקורס](https://github.com/paulavrahami/etl-course-demo), את [מדריך Windows ו־uv](https://github.com/paulavrahami/etl-course-demo/blob/main/WINDOWS_UV_START.md) ואת [מדריך ההתחלה](https://github.com/paulavrahami/etl-course-demo/blob/main/STUDENT_QUICKSTART.md). המחברת כבר נמצאת במאגר.

בקשו להשלים לפני השיעור את התקנת החבילות, בחירת ה־Kernel והרצת ההדגמה עד לחיפוש במסמכים. אם הסטודנטים אמורים לפתור את תרגיל הביקורות, מנחים אותם לעצור לפני חלק הפתרון למרצה.

לכיתה שבוחרת ב־Codespaces שולחים בנוסף את [קישור פתיחת הסביבה](https://codespaces.new/paulavrahami/etl-course-demo). כל סטודנט או זוג יוצר סביבת עבודה משלו.

במסלול Codespaces מבקשים להשלים לפני השיעור:

1. פתיחת חשבון GitHub או התחברות לחשבון קיים.
2. וידוא גישה למאגר ומכסת Codespaces זמינה.
3. פתיחת הסביבה והשלמת ההתקנה.
4. הרצת `python scripts/preflight.py` עד לסיום מוצלח.

חשבונות GitHub אישיים כוללים מכסת שימוש חודשית, בכפוף לתוכנית ולשימוש הקודם. אין להניח שלכל סטודנט נותרה מכסה. סביבת הפיתוח המצורפת מבקשת ארבע ליבות ו־8GB זיכרון. עצרו את הסביבה כשמסיימים לעבוד; שמירת סביבות קיימות צורכת אחסון.

## 4. תחילת התרגיל בכיתה

אחרי שההדגמה עובדת, כל זוג מריץ פעם אחת:

```bash
make exercise-start
```

לאחר כל שלב מפעילים את הבודק של אותו שלב, למשל:

```bash
python exercises/check_exercise.py 1
```

בסוף כל השלבים:

```bash
make check
```

הפקודה `exercise-start` מעתיקה קובצי התחלה; הרצה חוזרת עלולה להחליף את העבודה באותם קבצים. אין לשלוח לסטודנטים את פקודת `exercise-solution` כפקודת פתיחה.

## 5. מסלול הטרמינל הקיים ותרגול חלקי

הוראות הטרמינל ל־Windows, macOS ו־Linux נמצאות ב־`STUDENT_QUICKSTART.md`. מסלולי Python 3.11 ו־3.12 הקיימים עדיין זמינים. ב־macOS/Linux, אם הפקודה `python` אינה קיימת, יוצרים את הסביבה בעזרת `python3 -m venv .venv`; לאחר הפעלתה משתמשים ב־`python`. עבור Windows עם Python 3.13.12 משתמשים במסלול uv והמחברת שלמעלה.

אם הורדת רכיבי RAG מתעכבת, אפשר להתקדם במסלול הנתונים המובנים:

```bash
python scripts/setup_classroom.py --core-only
python scripts/preflight.py --core-only
```

מסלול הליבה אינו מאמת חיפוש סמנטי. להשלמת RAG יש להריץ את ההתקנה ואת בדיקת המוכנות המלאות. וקטורי hashing מדומים מיועדים לבדיקת צנרת בלבד.

## מקורות רשמיים

- [מחברות Jupyter וסביבות uv](https://docs.astral.sh/uv/guides/integration/jupyter/)
- [בחירת סביבת Python ב־uv](https://docs.astral.sh/uv/pip/environments/)
- [מחברות בתוך Cursor](https://cursor.com/for/data-science)
- [הגדרת פרויקט Python ב־Codespaces](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/setting-up-your-python-project-for-codespaces)
- [יצירת Codespace ממאגר](https://docs.github.com/en/codespaces/developing-in-a-codespace/creating-a-codespace-for-a-repository)
- [קישור פתיחה וכפתור Codespaces](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/setting-up-your-repository/facilitating-quick-creation-and-resumption-of-codespaces)
- [מכסת השימוש הכלולה בחשבון](https://docs.github.com/en/codespaces/troubleshooting/troubleshooting-included-usage)

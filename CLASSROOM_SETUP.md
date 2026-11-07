# הכנת הכיתה — מדריך קצר למרצה

המסלול המומלץ הוא GitHub Codespaces: סביבת דפדפן אישית לכל סטודנט או זוג. הקוד כולל גם מסלול התקנה מקומית. התרגול הבסיסי והחיפוש הסמנטי משתמשים בנתוני הדוגמה ובמודל מקומי; יצירת תשובה דרך ספק LLM היא הרחבה נפרדת.

## 1. מאגר הקורס

מאגר הקורס הציבורי: [paulavrahami/etl-course-demo](https://github.com/paulavrahami/etl-course-demo).

פתיחת סביבת תרגול: [GitHub Codespaces](https://codespaces.new/paulavrahami/etl-course-demo).

קובצי הפרויקט נמצאים בשורש המאגר: `README.md`, `Makefile`, `requirements.txt`, התיקיות `scripts`, `pipelines`, `dbt_project`, `exercises`, והגדרת סביבת הפיתוח `.devcontainer/devcontainer.json`. הגדרה זו מפעילה את ההתקנה האוטומטית בעת יצירת הסביבה.

משקלי המודל והסביבה הווירטואלית מותקנים בעת ההקמה. המאגר כולל את קובצי ההתחלה ואת פתרון התרגיל במלואו, לצורך הדגמה ובדיקה עצמית.

## 2. הרצת ניסיון בסביבה חדשה

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

שלחו לסטודנטים את [קישור פתיחת הסביבה](https://codespaces.new/paulavrahami/etl-course-demo) ואת [מדריך ההתחלה](https://github.com/paulavrahami/etl-course-demo/blob/main/STUDENT_QUICKSTART.md). כל סטודנט או זוג יוצר סביבת עבודה משלו.

בקשו להשלים לפני השיעור:

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

## 5. חלופה מקומית

הוראות Windows, macOS ו־Linux נמצאות ב־`STUDENT_QUICKSTART.md`. משתמשים ב־Python 3.11 או 3.12 ובסביבה וירטואלית. ב־macOS/Linux, אם הפקודה `python` אינה קיימת, יוצרים את הסביבה בעזרת `python3 -m venv .venv`; לאחר הפעלתה משתמשים ב־`python`.

אם הורדת רכיבי RAG מתעכבת, אפשר להתקדם במסלול הנתונים המובנים:

```bash
python scripts/setup_classroom.py --core-only
python scripts/preflight.py --core-only
```

מסלול הליבה אינו מאמת חיפוש סמנטי. להשלמת RAG יש להריץ את ההתקנה ואת בדיקת המוכנות המלאות. וקטורי hashing מדומים מיועדים לבדיקת צנרת בלבד.

## מקורות רשמיים

- [הגדרת פרויקט Python ב־Codespaces](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/setting-up-your-python-project-for-codespaces)
- [יצירת Codespace ממאגר](https://docs.github.com/en/codespaces/developing-in-a-codespace/creating-a-codespace-for-a-repository)
- [קישור פתיחה וכפתור Codespaces](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/setting-up-your-repository/facilitating-quick-creation-and-resumption-of-codespaces)
- [מכסת השימוש הכלולה בחשבון](https://docs.github.com/en/codespaces/troubleshooting/troubleshooting-included-usage)

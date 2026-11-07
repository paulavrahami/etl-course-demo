# קיצורי דרך. ב-Windows בלי make - העתיקו את הפקודות מכל יעד.
PY ?= python
DBT = cd dbt_project && dbt

.PHONY: setup setup-core data basic dlt dbt rag ask dagster demo demo-core preflight preflight-core exercise-start exercise-solution exercise-solution-core check clean

setup:            ## התקנה מלאה
	$(PY) scripts/setup_classroom.py

setup-core:       ## התקנת Python/dlt/dbt/Dagster בלי הורדת מודל RAG
	$(PY) scripts/setup_classroom.py --core-only

data:             ## יצירה מחדש של נתוני הדוגמה
	$(PY) scripts/generate_data.py

basic:            ## מודול 1: ETL ב-Python טהור
	$(PY) pipelines/01_pure_python_etl.py

dlt:              ## מודול 2: dlt -> DuckDB (אופליין)
	$(PY) pipelines/02_dlt_pipeline.py --offline

dbt:              ## מודול 3: dbt build (מודלים + בדיקות)
	$(DBT) build --profiles-dir .

rag:              ## מודול 4: אינדוקס מסמכים ל-LanceDB
	$(PY) pipelines/03_rag_pipeline.py

ask:              ## שאילתת דוגמה ל-RAG
	$(PY) pipelines/03_rag_pipeline.py --query "תוך כמה זמן אפשר להחזיר מוצר אלקטרוני?"

dagster:          ## מודול 5: Dagster UI על פורט 3000
	$(PY) scripts/start_dagster.py

demo: basic dlt dbt rag ask   ## כל ההדגמה ברצף

demo-core: basic dlt dbt     ## ההדגמה המובנית, ללא RAG

preflight:         ## בדיקת מוכנות לפני השיעור
	$(PY) scripts/preflight.py

preflight-core:    ## בדיקת מוכנות ללא RAG
	$(PY) scripts/preflight.py --core-only

exercise-start:   ## מעתיק את קבצי ה-starter של התרגיל למקומם
	cp exercises/starter/04_reviews_pipeline.py exercises/starter/05_reviews_rag.py pipelines/
	cp exercises/starter/stg_reviews.sql dbt_project/models/staging/
	cp exercises/starter/mart_product_reviews.sql dbt_project/models/marts/
	cp exercises/starter/_reviews.yml dbt_project/models/marts/

exercise-solution-core: ## (למרצה) פתרון שלבים 1–3, גם מתיקייה חדשה
	cp exercises/solution/04_reviews_pipeline.py exercises/solution/05_reviews_rag.py pipelines/
	cp exercises/solution/stg_reviews.sql dbt_project/models/staging/
	cp exercises/solution/mart_product_reviews.sql dbt_project/models/marts/
	cp exercises/solution/_reviews.yml dbt_project/models/marts/
	$(PY) pipelines/02_dlt_pipeline.py --offline
	$(PY) pipelines/04_reviews_pipeline.py
	$(DBT) build --profiles-dir .
	$(PY) exercises/check_exercise.py 1 2 3

exercise-solution: exercise-solution-core ## (למרצה) פתרון מלא כולל RAG ובודק
	$(PY) pipelines/05_reviews_rag.py
	$(PY) exercises/check_exercise.py

check:            ## בדיקת התרגיל
	$(PY) exercises/check_exercise.py

clean:            ## מחיקת כל התוצרים (מתחילים מאפס)
	rm -rf warehouse.duckdb* warehouse_basic.db lancedb dbt_project/target dbt_project/logs .dlt/pipelines
	rm -f pipelines/04_reviews_pipeline.py pipelines/05_reviews_rag.py dbt_project/models/staging/stg_reviews.sql \
	      dbt_project/models/marts/mart_product_reviews.sql dbt_project/models/marts/_reviews.yml

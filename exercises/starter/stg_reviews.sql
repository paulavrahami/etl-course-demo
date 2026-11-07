-- תרגיל כיתה - שלב 2: ניקוי ביקורות
-- ================================================
-- כללים עסקיים:
--   1. דירוג חוקי הוא 1 עד 5 בלבד (יש 0, 7 ו-null בנתונים)
--   2. ביקורת עם טקסט ריק או רק רווחים - לא נכנסת
--   3. יש ביקורות כפולות (אותו review_id) - שורה אחת לכל ביקורת
--
-- רמזים:  stg_customers.sql משתמש ב-qualify row_number() ...
--         איך נקראת עמודת המוצר אחרי ש-dlt טען את {"product": {"id": 3}} ?
--
-- הרצה:  cd dbt_project && dbt build --select stg_reviews --profiles-dir .
-- בדיקה: python exercises/check_exercise.py 2

with source as (
    select * from {{ source('raw', 'reviews') }}
)

select
    cast(review_id as integer)      as review_id,
    cast(order_id as integer)       as order_id,
    -- TODO: product_id
    -- TODO: rating (כ-integer)
    -- TODO: review_text (טקסט מנוקה; ריק -> null)
    cast(created_at as timestamp)   as created_at
from source
-- TODO: סינון לפי הכללים העסקיים
-- TODO: דה-דופליקציה

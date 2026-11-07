-- תרגיל כיתה - שלב 3: טבלת mart לכל מוצר
-- ================================================
-- שורה אחת לכל מוצר (כל 8 המוצרים, גם בלי ביקורות!) עם העמודות:
--   product_id, product_name, category,
--   review_count, avg_rating (מעוגל ל-2 ספרות), negative_reviews (דירוג <= 2),
--   paid_orders, revenue (רק הזמנות בסטטוס paid, מתוך fct_orders)
--
-- רמז: שני CTE-ים (ביקורות, מכירות) ו-left join מ-stg_products
-- בדיקה: python exercises/check_exercise.py 3

-- TODO
select 1 as todo

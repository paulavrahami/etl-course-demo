-- תרגיל כיתה - שלב 2: ניקוי ביקורות   [פתרון]
with source as (
    select * from {{ source('raw', 'reviews') }}
),

typed as (
    select
        cast(review_id as integer)      as review_id,
        cast(order_id as integer)       as order_id,
        cast(product__id as integer)    as product_id,     -- dlt "שיטח" את product.id
        cast(rating as integer)         as rating,
        nullif(trim(text), '')          as review_text,
        cast(created_at as timestamp)   as created_at
    from source
)

select *
from typed
where rating between 1 and 5          -- דירוג לא חוקי (0, 7, null) נזרק
  and review_text is not null         -- טקסט ריק נזרק
qualify row_number() over (partition by review_id order by created_at) = 1   -- דה-דופליקציה

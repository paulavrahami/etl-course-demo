-- תרגיל כיתה - שלב 3: מדדי ביקורות + הכנסות לכל מוצר   [פתרון]
with review_stats as (
    select
        product_id,
        count(*)                                  as review_count,
        round(avg(rating), 2)                     as avg_rating,
        count(*) filter (where rating <= 2)       as negative_reviews
    from {{ ref('stg_reviews') }}
    group by product_id
),

sales as (
    select
        product_id,
        count(*) filter (where status = 'paid')               as paid_orders,
        coalesce(sum(amount) filter (where status = 'paid'), 0) as revenue
    from {{ ref('fct_orders') }}
    group by product_id
)

select
    p.product_id,
    p.product_name,
    p.category,
    coalesce(r.review_count, 0)       as review_count,
    r.avg_rating,
    coalesce(r.negative_reviews, 0)   as negative_reviews,
    coalesce(s.paid_orders, 0)        as paid_orders,
    coalesce(s.revenue, 0)            as revenue
from {{ ref('stg_products') }} p
left join review_stats r using (product_id)
left join sales s using (product_id)
order by revenue desc

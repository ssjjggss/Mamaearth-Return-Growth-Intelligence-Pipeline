USE Mamaearth_Returns;
-- a) Order totals--
SELECT
    COUNT(*) AS total_orders,
    ROUND(
        SUM(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100)
        ),
        2
    ) AS total_revenue,
    ROUND(
        AVG(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100)
        ),
        2
    ) AS avg_order_value
FROM orders o
JOIN products p
    ON o.product_id = p.product_id;


-- b) COUNT(*) vs COUNT(column)-- 
select count(*) as Total_Col,count(rating) as Total_Rating,count(*)-count(rating) as order_NoRating
from orders;

-- LEFT JOIN with a genuine zero-match row 
select c.customer_id,c.name from customers c 
left join orders o
on c.customer_id=o.customer_id
group by
	c.customer_id,
	c.name 
having ((count(o.order_id)=0));


-- d) GROUP BY + HAVING 
select c.city as CITY,
count(*) as TOTAL_COUNT,
sum(o.returned) as TOTAL_RETURNED, 
((sum(o.returned)/count(*))*100)  as Return_Rate_Pct 
from orders o
join customers c
on o.customer_id = c.customer_id
group by c.city
having return_rate_pct > 20
order by return_rate_pct desc;

-- Ranking with ORDER BY + LIMIT/OFFSET  
select c.customer_id,c.name,round(sum(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100)),2) as total_spend from orders o 
join products p on p.product_id= o.product_id
join customers c on c.customer_id = o.customer_id
group by c.customer_id
order by total_spend desc,o.customer_id asc

limit 5-- 
-- limit 3 offset 2
;

-- Three-table
select 
p.category,
count(o.order_id),
round(
	sum(
		o.quantity * p.price *(1-COALESCE(o.discount_pct,0)/100.0)),2) as category_revenue
from orders o
join products p on o.product_id = p.product_id
join customers c on c.customer_id = o.customer_id
group by p.category
order by category_revenue desc;

-- g) LIKE pattern matc
select name from customers
where name like "A%";
-- h) DISTINCT 
select distinct acquisition_source from customers;

-- i) ALTER TABLE + UPDATE with
select 
case
	when city_tier = 1 then "gold" else "Silver" end as loyalty_tier ,
    count(*)
from customers
group by loyalty_tier;
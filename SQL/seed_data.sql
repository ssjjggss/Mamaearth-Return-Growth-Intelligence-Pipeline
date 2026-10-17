USE Mamaearth_Returns;


SELECT COUNT(*) FROM customers; -- 45
SELECT COUNT(*) FROM products; -- 16
SELECT COUNT(*) FROM orders; -- 180 

SET SQL_SAFE_UPDATES = 0;

UPDATE orders
SET discount_pct = NULL
WHERE TRIM(discount_pct) = '';

SET SQL_SAFE_UPDATES = 1;


SELECT * FROM orders_staging WHERE rating = '' LIMIT 5;
UPDATE orders SET discount_pct = NULL WHERE discount_pct = '';
UPDATE orders SET rating = NULL WHERE rating = '';
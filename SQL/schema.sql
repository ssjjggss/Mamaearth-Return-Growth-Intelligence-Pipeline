create database Mamaearth_Returns;
USE Mamaearth_Returns;
CREATE TABLE customers
(	customer_id  VARCHAR(10) PRIMARY KEY,
	name VARCHAR(50) NOT NULL, 
	city VARCHAR(50) NOT NULL,
	city_tier INT NOT NULL,
	signup_date DATE NOT NULL,
	acquisition_source VARCHAR(20) NOT NULL
 );
 
 
 select count(*) from customers;
 DROP TABLE IF exists products;
 create table products(
	product_id VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(30) NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

select count(*) from products;
DROP TABLE IF exists orders;
CREATE TABLE orders(
    order_id VARCHAR(10) PRIMARY KEY,
    customer_id VARCHAR(10) NOT NULL, 
    product_id VARCHAR(10) NOT NULL,
    order_date DATE NOT NULL, 
    quantity INT NOT NULL,
    discount_pct INT ,
    payment_method VARCHAR(10) NOT NULL,
    rating INT ,
    returned INT NOT NULL DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);


select count(*) from orders;
CREATE TABLE orders_staging (
    order_id VARCHAR(10),
    customer_id VARCHAR(10),
    product_id VARCHAR(10),
    order_date VARCHAR(20),
    quantity VARCHAR(10),
    discount_pct VARCHAR(10),
    payment_method VARCHAR(10),
    rating VARCHAR(10),
    returned VARCHAR(10)
);

select COUNT(*) from orders_staging;

INSERT INTO orders (order_id, customer_id, product_id, order_date, quantity,
                     discount_pct, payment_method, rating, returned)
SELECT
    order_id,
    customer_id,
    product_id,
    STR_TO_DATE(order_date, '%Y-%m-%d'),
    CAST(quantity AS UNSIGNED),
    NULLIF(discount_pct, ''),
    UPPER(payment_method),
    NULLIF(rating, ''),
    CAST(returned AS UNSIGNED)
FROM orders_staging;



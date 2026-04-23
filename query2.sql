-- ===============================
-- BASIC SELECT
-- ===============================
SELECT * FROM users;
SELECT name, age FROM users;

-- ===============================
-- WHERE CONDITIONS
-- ===============================
SELECT * FROM users WHERE age > 25;
SELECT * FROM users WHERE age >= 30;
SELECT * FROM users WHERE age < 40;
SELECT * FROM users WHERE age <= 50;
SELECT * FROM users WHERE age = 25;
SELECT * FROM users WHERE city != 'Mumbai';

-- ===============================
-- LOGICAL OPERATORS
-- ===============================
SELECT * FROM users WHERE age > 25 AND city = 'Delhi';
SELECT * FROM users WHERE age > 25 OR city = 'Mumbai';
SELECT * FROM users WHERE age > 25 AND city != 'Delhi';

-- ===============================
-- IN + BETWEEN
-- ===============================
SELECT * FROM users WHERE city IN ('Delhi', 'Hyderabad');
SELECT * FROM users WHERE age BETWEEN 20 AND 30;

-- ===============================
-- ORDER BY + LIMIT
-- ===============================
SELECT * FROM users ORDER BY age;
SELECT * FROM users ORDER BY age DESC;
SELECT * FROM users LIMIT 3;
SELECT * FROM users ORDER BY age DESC LIMIT 5;

-- ===============================
-- PROJECTION
-- ===============================
SELECT name FROM users;
SELECT name, city FROM users;

-- ===============================
-- AGGREGATION
-- ===============================
SELECT COUNT(*) FROM users;
SELECT SUM(age) FROM users;
SELECT AVG(age) FROM users;
SELECT MIN(age) FROM users;
SELECT MAX(age) FROM users;

-- ===============================
-- GROUP BY
-- ===============================
SELECT city, COUNT(*) FROM users GROUP BY city;
SELECT city, COUNT(*) FROM users GROUP BY city ORDER BY COUNT(*) DESC;
SELECT city, age, COUNT(*) FROM users GROUP BY city, age;

-- ===============================
-- HAVING
-- ===============================
SELECT city, COUNT(*) FROM users GROUP BY city HAVING COUNT(*) > 1;

-- ===============================
-- JOINS
-- ===============================
SELECT users.name, orders.amount
FROM users
JOIN orders ON users.id = orders.user_id;

SELECT users.name, orders.amount
FROM users
JOIN orders ON users.id = orders.user_id
WHERE orders.amount > 100;


-- ===============================
-- SUBQUERY
-- ===============================
SELECT name FROM users
WHERE id IN (
    SELECT user_id FROM orders WHERE amount > 100
);

-- ===============================
-- MULTIPLE QUERIES
-- ===============================
SELECT * FROM users;
SELECT * FROM orders;
SELECT name FROM users WHERE age > 25;

-- ===============================
-- MULTI-LINE QUERY
-- ===============================
SELECT name, age
FROM users
WHERE age > 25
ORDER BY age DESC;


-- ===============================
-- ERROR TEST CASES
-- ===============================
SELECT FROM users;
SELECT name users;
SELECT * FROM unknown_table;
SELECT * FROM users WHERE age >> 25;
SELECT COUNT( FROM users;

-- ===============================
-- EDGE CASES
-- ===============================
SELECT * FROM users WHERE age = 0;
SELECT * FROM users WHERE city = '';
SELECT * FROM users LIMIT 0;
SELECT city, COUNT(*) FROM users GROUP BY city HAVING COUNT(*) = 0;

-- ===============================
-- ===============================
-- OPTIMIZATION TEST CASES
-- ===============================
-- ===============================

-- -------------------------------
-- 1. OR → IN optimization
-- -------------------------------
SELECT * FROM users 
WHERE city = 'Delhi' OR city = 'Hyderabad' OR city = 'Mumbai';

-- Expected optimization:
-- { city: { $in: ['Delhi','Hyderabad','Mumbai'] } }

-- -------------------------------
-- 2. Duplicate OR values
-- -------------------------------
SELECT * FROM users 
WHERE city = 'Delhi' OR city = 'Delhi' OR city = 'Mumbai';

-- Expected:
-- duplicates removed → $in with unique values

-- -------------------------------
-- 3. RANGE OPTIMIZATION (OR → GT)
-- -------------------------------
SELECT * FROM users 
WHERE age > 20 OR age > 25 OR age > 30;

-- Expected:
-- age > 20 (smallest)

-- -------------------------------
-- 4. RANGE OPTIMIZATION (OR → LT)
-- -------------------------------
SELECT * FROM users 
WHERE age < 50 OR age < 40 OR age < 30;

-- Expected:
-- age < 50 (largest)

-- -------------------------------
-- 5. AND MERGE
-- -------------------------------
SELECT * FROM users 
WHERE age > 25 AND age < 40;

-- Expected:
-- { age: { $gt: 25, $lt: 40 } }



-- -------------------------------
-- 8. IN ORDER NORMALIZATION
-- -------------------------------
SELECT * FROM users 
WHERE city IN ('Mumbai', 'Delhi', 'Delhi', 'Hyderabad');

-- Expected:
-- sorted + unique values

-- -------------------------------
-- 9. MULTIPLE MATCH (AGGREGATE OPT)
-- -------------------------------
SELECT city, COUNT(*) 
FROM users 
WHERE age > 25
GROUP BY city;

-- Expected:
-- $match pushed before $group

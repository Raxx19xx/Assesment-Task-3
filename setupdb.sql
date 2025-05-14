-------------------------------------------------------
-- NOTICE the DECIMAL(10, 2) and date data types
-- ALSO the FOREIGN KEY (user_id) REFERENCES users(id) 
-------------------------------------------------------

-- Drop tables if they exist to avoid conflicts during re-initialisation
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstname TEXT NOT NULL
);

-- Create products table
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    stock_level INTEGER NOT NULL,
    cost DECIMAL(10, 2) NOT NULL
);

-- Create orders table
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    date TEXT DEFAULT CURRENT_TIMESTAMP,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
-- FOREIGN KEY (user_id) REFERENCES users(id) enforces referential integrity, meaning you 
-- can’t add an order for a user that doesn’t exist, similarily for
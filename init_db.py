import sqlite3, os

DB_PATH = 'mydb.db'
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT,
    mobile TEXT,
    address TEXT,
    profile_image TEXT
)
''')

cur.execute('''
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    stock_level INTEGER NOT NULL,
    cost REAL NOT NULL
)
''')

cur.execute('''
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

cur.execute('''
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
)
''')

# Insert your products
cur.executemany(
    "INSERT INTO products (name, stock_level, cost) VALUES (?, ?, ?)",
    [
        ("Global Travel eSIM 5GB", 45, 19.99),
        ("Global Travel eSIM 20GB", 200, 29.99),
        ("Global Travel eSIM 50GB", 80, 39.99),
        ("Global Travel eSIM Unlimited", 80, 49.99),
    ]
)

conn.commit()
conn.close()
print("Database initialized!")
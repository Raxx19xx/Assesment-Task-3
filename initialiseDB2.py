import sqlite3

def initialise_data(db_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # CLEAN SLATE (optional): Remove previous test data
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM users")
        
        # Insert users
        cursor.execute("INSERT INTO users (firstname) VALUES (?)", ("Fred",))
        cursor.execute("INSERT INTO users (firstname) VALUES (?)", ("Joe",))

        # Insert YOUR products
        cursor.execute("INSERT INTO products (name, stock_level, cost) VALUES (?, ?, ?)", ("Global Travel eSIM 5GB", 45, 19.99))
        cursor.execute("INSERT INTO products (name, stock_level, cost) VALUES (?, ?, ?)", ("Global Travel eSIM 20GB", 200, 29.99))
        cursor.execute("INSERT INTO products (name, stock_level, cost) VALUES (?, ?, ?)", ("Global Travel eSIM 50GB", 80, 39.99))
        cursor.execute("INSERT INTO products (name, stock_level, cost) VALUES (?, ?, ?)", ("Global Travel eSIM Unlimited", 80, 49.99))
        
        # Get user and product IDs (to create some orders if you want)
        cursor.execute("SELECT id FROM users WHERE firstname = ?", ("Fred",))
        fred_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM users WHERE firstname = ?", ("Joe",))
        joe_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM products WHERE name = ?", ("Sweater",))
        sweater_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM products WHERE name = ?", ("Cap",))
        cap_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM products WHERE name = ?", ("Sneakers",))
        sneakers_id = cursor.fetchone()[0]

        # Insert orders (optional, with your new products)
        cursor.execute("INSERT INTO orders (user_id, product_id, date, quantity) VALUES (?, ?, ?, ?)", 
                       (fred_id, sweater_id, "2025-05-01", 10))
        cursor.execute("INSERT INTO orders (user_id, product_id, date, quantity) VALUES (?, ?, ?, ?)", 
                       (joe_id, cap_id, "2025-05-02", 20))
        cursor.execute("INSERT INTO orders (user_id, product_id, date, quantity) VALUES (?, ?, ?, ?)", 
                       (joe_id, sneakers_id, "2025-05-03", 5))

        conn.commit()
        print("Data in database initialised successfully with YOUR products.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
    
# Run this script to INITIALISE WITH YOUR PRODUCTS
# initialise_data("databasew.db")
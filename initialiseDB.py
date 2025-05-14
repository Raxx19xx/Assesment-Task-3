#
# REVIEW THE  "SELECT id FROM users WHERE firstname = ?", ("Fred",)
# ETC so that the 'foreign key' relationships are valid for the test data
#

import sqlite3

def execute_sql(file_path, db_name):
    try:
        # Connect to the SQLite database (creates it if it doesn't exist)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Read SQL file
        with open(file_path, 'r') as file:
            sql_script = file.read()
        
        # Execute SQL script
        cursor.executescript(sql_script)
        conn.commit()
        print("Database initialised successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

# Run this script to SETUP your database
# execute_sql("setupdb.sql", "mydb.db")

def initialise_data(db_name):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Insert users
        cursor.execute("INSERT INTO users (firstname) VALUES (?)", ("Fred",))
        cursor.execute("INSERT INTO users (firstname) VALUES (?)", ("Joe",))

        # Insert products
        cursor.execute("INSERT INTO products (name, stock_level, cost) VALUES (?, ?, ?)", ("Tee Shirt", 100, 20.00))
        cursor.execute("INSERT INTO products (name, stock_level, cost) VALUES (?, ?, ?)", ("Jeans", 58, 40.00))
        
        # Get user and product IDs
        cursor.execute("SELECT id FROM users WHERE firstname = ?", ("Fred",))
        fred_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM users WHERE firstname = ?", ("Joe",))
        joe_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM products WHERE name = ?", ("Tee Shirt",))
        tee_shirt_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM products WHERE name = ?", ("Jeans",))
        jeans_id = cursor.fetchone()[0]

        # Insert orders
        cursor.execute("INSERT INTO orders (user_id, product_id, date, quantity) VALUES (?, ?, ?, ?)", 
                       (fred_id, tee_shirt_id, "2025-04-02", 50))
        cursor.execute("INSERT INTO orders (user_id, product_id, date, quantity) VALUES (?, ?, ?, ?)", 
                       (joe_id, tee_shirt_id, "2025-04-03", 43))
        cursor.execute("INSERT INTO orders (user_id, product_id, date, quantity) VALUES (?, ?, ?, ?)", 
                       (joe_id, jeans_id, "2025-05-04", 100))

        # Commit the transactions
        conn.commit()
        print("Data in database initialised successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
    
# Run this script to INITIALISE WITH DUMMY DATA in your database
# initialise_data("mydb.db")
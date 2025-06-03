from flask import Flask, render_template, request, redirect, session, url_for
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'mydb.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def is_strong_password(password):
    if len(password) < 12 or len(password) > 20: return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[a-z]", password): return False
    if not re.search(r"\d", password): return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): return False
    return True

# Home Page

@app.route("/")
def home():
    return render_template("index.html")

# Signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        role = 'user'
        mobile = request.form['mobile']
        address = request.form['address']
        if not is_strong_password(password):
            return render_template("signup.html", error="Password must be 12–20 characters long and include upper, lower, digit, and special character.")
        hashed_pw = generate_password_hash(password)
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password, role, mobile, address) VALUES (?, ?, ?, ?, ?)", (username, hashed_pw, role, mobile, address))
            conn.commit()
        except Exception as e:
            return render_template("signup.html", error=f"Signup failed: {e}")
        finally:
            conn.close()
        return redirect("/")
    return render_template("signup.html")

# Login
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password, role FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session['username'] = username
            session['role'] = user["role"]
            session['user_id'] = user["id"]
            session['cart'] = {}
            return redirect(url_for('home'))
        else:
            return render_template("login.html", error="Login failed. Check your credentials.")
    return render_template("login.html")

# User dashboard
@app.route("/user")
def user_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("user_dashboard.html", username=session['username'])

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# --- Products and Cart ---
@app.route("/products")
def products():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.route("/add_to_cart/<int:product_id>", methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get("quantity", 1))
    cart = session.get("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    if 'username' not in session:
        return redirect(url_for('login'))
    cart = session.get("cart", {})
    if not cart:
        return render_template("cart.html", cart_items=[], total=0)
    conn = get_db_connection()
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = conn.execute('SELECT * FROM products WHERE id=?', (pid,)).fetchone()
        if product:
            item_total = product['cost'] * qty
            total += item_total
            cart_items.append({'id': product['id'], 'name': product['name'], 'cost': product['cost'], 'quantity': qty, 'item_total': item_total})
    conn.close()
    return render_template("cart.html", cart_items=cart_items, total=total)

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)
    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/checkout", methods=['POST'])
def checkout():
    if 'username' not in session:
        return redirect(url_for('login'))
    cart = session.get("cart", {})
    if not cart:
        return redirect(url_for('cart'))
    conn = get_db_connection()
    cur = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute("INSERT INTO orders (user_id, order_date) VALUES (?, ?)", (session['user_id'], now))
    order_id = cur.lastrowid
    for pid, qty in cart.items():
        cur.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)", (order_id, pid, qty))
        cur.execute("UPDATE products SET stock_level = stock_level - ? WHERE id = ?", (qty, pid))
    conn.commit()
    conn.close()
    session["cart"] = {}
    return redirect(url_for("orders"))

@app.route("/orders")
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    orders = conn.execute("SELECT * FROM orders WHERE user_id=? ORDER BY order_date DESC", (session['user_id'],)).fetchall()
    order_list = []
    for order in orders:
        items = conn.execute('''
            SELECT products.name, order_items.quantity, products.cost
            FROM order_items
            JOIN products ON order_items.product_id = products.id
            WHERE order_items.order_id=?
        ''', (order['id'],)).fetchall()
        order_list.append({'id': order['id'], 'date': order['order_date'], 'items': items})
    conn.close()
    return render_template('orders.html', orders=order_list)


if __name__ == "__main__":
    app.run(debug=True)

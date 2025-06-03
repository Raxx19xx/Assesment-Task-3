from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
import sqlite3
import logging
import os
import re

# Initialize the Flask app
app = Flask(__name__)

# --- Configurations ---
app.secret_key = 'super-secret-key'  # Used to sign session cookies
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions on the filesystem
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Where profile images are stored
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Make the folder if it doesn't exist
Session(app)  # Enable session management

csrf = CSRFProtect(app)

# Rate limiting setup to protect against brute-force attacks
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"], storage_uri="memory://")

# Logging setup to file for security events
file_handler = logging.FileHandler('security_log.log')
file_handler.setLevel(logging.WARNING)
app.logger.addHandler(file_handler)

# --- Database Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'mydb.db')  # Path to your database file

# Function to open a connection to the SQLite database
def get_db_connection():
    return sqlite3.connect(DB_PATH, timeout=10)

# --- Password Strength Checker ---
def is_strong_password(password):
    # Check various conditions to ensure password strength
    print("Checking password strength:", password)
    if len(password) < 12 or len(password) > 20:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

# --- Routes ---
# Home page
@app.route("/")
def home():
    # Redirect user to their dashboard if already logged in
    if 'username' in session:
        return redirect(url_for('user_dashboard')) if session.get('role') == 'user' else redirect(url_for('admin_dashboard'))
    return render_template("index4.html")

# Signup route for new users
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Extract form data
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'user')
        mobile = request.form['mobile']
        address = request.form['address']
        profile = request.files['profile']

        # Validate password strength
        if not is_strong_password(password):
            return render_template("signup.html", error="Password must be 12–20 characters long and include upper, lower, digit, and special character.")

        # Hash the password
        hashed_pw = generate_password_hash(password)

        # Save profile image with a unique name
        profile_filename = None
        if profile:
            profile_filename = f"{username}_{profile.filename}"
            profile_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_filename)
            profile.save(profile_path)

        # Store user in database
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (username, password, role, mobile, address, profile_image)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, hashed_pw, role, mobile, address, profile_filename))
            conn.commit()
        except Exception as e:
            return f"Signup failed due to: {e}"
        finally:
            conn.close()

        return redirect("/")  # Redirect to login/home after signup

    return render_template("signup.html")

# Login route for existing users
@app.route("/login", methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Limit login attempts

def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT password, role FROM users WHERE username = ?", (username,))
            user = cur.fetchone()
        finally:
            conn.close()

        # Validate the password
        if user and check_password_hash(user[0], password):
            session['username'] = username
            session['role'] = user[1]
            return redirect("/admin") if user[1] == 'admin' else redirect("/user")
        else:
            app.logger.warning(f"Failed login attempt for {username}")
            return render_template("login.html", error="Login failed. Check your credentials.")

    return render_template("login.html")

# Forgot password form (demo version)
@app.route("/forgot-password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == "POST":
        username_or_mobile = request.form['username_or_mobile']
        return render_template("forgot_password.html", message=f"Reset instructions sent for: {username_or_mobile}")
    return render_template("forgot_password.html")

# Admin dashboard (role protected)
@app.route("/admin")
def admin_dashboard():
    if 'username' in session and session.get('role') == 'admin':
        return render_template("admin_dashboard.html", username=session['username'])
    return redirect("/")

# User dashboard (role protected)
@app.route("/user")
def user_dashboard():
    if 'username' in session and session.get('role') == 'user':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT mobile, address, profile_image FROM users WHERE username = ?", (session['username'],))
            user_data = cur.fetchone()
        finally:
            conn.close()

        return render_template("user_dashboard.html", username=session['username'], mobile=user_data[0], address=user_data[1], profile=user_data[2])
    return redirect("/")

# Logout route to clear session
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# --- Error Handling ---
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html"), 500

@app.errorhandler(Exception)
def catch_all(e):
    app.logger.error(f"Unhandled Exception: {str(e)}")
    return render_template("500.html"), 500


# Run the Flask development server
if __name__ == "__main__":
    app.run(debug=False)


def get_db_connection():
    conn = sqlite3.connect('mydb.db')
    conn.row_factory = sqlite3.Row
    return conn
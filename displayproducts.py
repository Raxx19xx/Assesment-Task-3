from flask import Flask, jsonify, render_template
import sqlite3

app = Flask(__name__)

@app.route('/displayproducts', methods=['GET'])
def displayProducts():
    conn = get_db_connection()
    allproducts = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('displayproducts.html', allproducts=allproducts)

@app.route('/displayorders', methods=['GET'])
def displayOrders():
    conn = get_db_connection()
    allorders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return render_template('displayorders.html', allorders=allorders)

def get_db_connection():
    conn = sqlite3.connect('mydb.db')
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == '__main__':
    app.run(debug=True)
    
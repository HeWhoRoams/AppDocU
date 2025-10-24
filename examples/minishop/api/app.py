# MiniShop API Layer
# Python Flask application

import json
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# External API calls
def call_payment_service(amount, card_info):
    """Calls external payment API"""
    response = requests.post("https://payment-api.example.com/charge", 
                           json={"amount": amount, "card": card_info})
    return response.json()

def call_inventory_service(product_id):
    """Calls external inventory API"""
    try:
        response = requests.get(f"https://inventory-api.example.com/products/{product_id}",
                               timeout=5.0)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Inventory service call failed: {e}")
@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products"""
    # Reads from database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return jsonify(products)

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    order_data = request.json
    
    # Writes to database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (user_id, product_id, quantity) VALUES (?, ?, ?)",
                   (order_data['user_id'], order_data['product_id'], order_data['quantity']))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Calls external payment service
    payment_result = call_payment_service(
        order_data['amount'], 
        order_data['card_info']
    )
    
    return jsonify({"order_id": order_id, "payment_status": payment_result['status']})

def get_db_connection():
    """Database connection"""
    import sqlite3
    conn = sqlite3.connect('minishop.db')
    return conn

if __name__ == '__main__':
    app.run(debug=True)

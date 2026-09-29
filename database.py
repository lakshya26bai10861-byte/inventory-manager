"""
database.py
------------
The storage room of our Inventory Manager.
All SQLite database work lives here.

We keep three tables:
  - users     → who's using the app (admin/staff)
  - products  → what we stock
  - sales     → what we sold

SQLite is built into Python, so no installation required.
"""

import sqlite3

DB_NAME = "inventory.db"


def get_connection():
    """
    Opens a connection to the database file.
    Creates the file automatically if it doesn't exist.
    """
    conn = sqlite3.connect(DB_NAME)
    # This lets us use column names like row["product_name"]
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    """
    Creates our three tables if they don't already exist.
    Safe to run every time the app starts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # --- Users table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'staff',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- Products table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            reorder_level INTEGER DEFAULT 5,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- Sales table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            sale_date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database ready!")


# =============== USER HELPERS ===============

def add_user(username, password, role="staff"):
    """Saves a new user. Returns False if username already exists."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def get_user(username, password):
    """Returns user row if credentials match, else None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()
    return user


# =============== PRODUCT HELPERS ===============

def add_product(name, category, price, quantity, reorder_level):
    """Adds a new product to inventory."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, category, price, quantity, reorder_level)
        VALUES (?, ?, ?, ?, ?)
    """, (name, category, price, quantity, reorder_level))
    conn.commit()
    conn.close()


def get_products():
    """Returns all products, alphabetical."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_product_by_id(product_id):
    """Fetch one specific product."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def update_product_quantity(product_id, new_quantity):
    """Updates the stock level for a product."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET quantity = ? WHERE id = ?",
        (new_quantity, product_id)
    )
    conn.commit()
    conn.close()


def delete_product(product_id):
    """Removes a product from inventory."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


# =============== SALES HELPERS ===============

def add_sale(product_id, quantity, total_price, sale_date):
    """Records a sale."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sales (product_id, quantity, total_price, sale_date)
        VALUES (?, ?, ?, ?)
    """, (product_id, quantity, total_price, sale_date))
    conn.commit()
    conn.close()


def get_sales():
    """Returns all sales with product names joined in."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, p.name AS product_name, s.quantity,
               s.total_price, s.sale_date
        FROM sales s
        JOIN products p ON p.id = s.product_id
        ORDER BY s.sale_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows
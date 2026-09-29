"""
products.py
------------
Module 2: Product & Stock Management.
Handles adding, updating, and deleting products,
plus recording sales (which reduces stock).
"""

from database import (
    add_product, get_products, get_product_by_id,
    update_product_quantity, delete_product,
    add_sale, get_sales,
)


# Categories used in the dropdown
CATEGORIES = ["Electronics", "Groceries", "Stationery", "Clothing", "Other"]


def create_product(name, category, price, quantity, reorder_level):
    """
    Validates and saves a new product.
    Returns (success, message).
    """
    if not name.strip():
        return False, "Product name cannot be empty."

    if category not in CATEGORIES:
        return False, "Please pick a valid category."

    # Price check
    try:
        price = float(price)
        if price <= 0:
            return False, "Price must be greater than 0."
    except ValueError:
        return False, "Price must be a number."

    # Quantity check
    try:
        quantity = int(quantity)
        if quantity < 0:
            return False, "Quantity cannot be negative."
    except ValueError:
        return False, "Quantity must be a whole number."

    # Reorder level check
    try:
        reorder_level = int(reorder_level)
        if reorder_level < 0:
            reorder_level = 0
    except ValueError:
        reorder_level = 5

    add_product(name.strip(), category, price, quantity, reorder_level)
    return True, "Product added!"


def list_products():
    """Return all products."""
    return get_products()


def remove_product(product_id):
    """Delete a product by id."""
    delete_product(product_id)
    return True, "Product removed."


def sell_product(product_id, quantity, sale_date):
    """
    Records a sale and reduces stock.
    Returns (success, message).
    """
    product = get_product_by_id(product_id)
    if not product:
        return False, "Product not found."

    try:
        quantity = int(quantity)
        if quantity <= 0:
            return False, "Quantity must be greater than 0."
    except ValueError:
        return False, "Quantity must be a whole number."

    if quantity > product["quantity"]:
        return False, f"Only {product['quantity']} units in stock."

    total = round(quantity * product["price"], 2)

    # Save the sale
    add_sale(product_id, quantity, total, sale_date)

    # Reduce stock
    new_qty = product["quantity"] - quantity
    update_product_quantity(product_id, new_qty)

    return True, f"Sale recorded: ₹{total:.2f}"


def list_sales():
    """Return all sales."""
    return get_sales()

from database import Database
from datetime import datetime
import sqlite3


class InventoryManager:

    def __init__(self):
        self.db = Database()

    # =====================================
    # 1. ADD NEW PRODUCT
    # =====================================

    def add_product(self, sku, name, category,
                    supplier_id, quantity, reorder_level,
                    unit_cost, selling_price, description=""):

        if not sku.strip() or not name.strip():
            raise ValueError("SKU and product name are required.")

        if quantity < 0 or reorder_level < 0:
            raise ValueError("Quantity and reorder level cannot be negative.")

        if unit_cost < 0 or selling_price < 0:
            raise ValueError("Prices cannot be negative.")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.db.connect() as conn:

            cursor = conn.execute("""
                INSERT INTO products
                (
                    sku, name, category, supplier_id,
                    quantity, reorder_level, unit_cost,
                    selling_price, description,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sku.strip(),
                name.strip(),
                category,
                supplier_id,
                quantity,
                reorder_level,
                unit_cost,
                selling_price,
                description,
                now,
                now
            ))

            product_id = cursor.lastrowid

            # Record opening stock
            if quantity > 0:

                conn.execute("""
                    INSERT INTO transactions
                    (
                        product_id, transaction_type,
                        quantity, note, transaction_date
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    product_id,
                    "STOCK IN",
                    quantity,
                    "Opening stock",
                    now
                ))

        print("Product added successfully!")

        return product_id

    # =====================================
    # 2. DISPLAY ALL PRODUCTS
    # =====================================

    def get_all_products(self):

        with self.db.connect() as conn:

            products = conn.execute("""
                SELECT
                    products.*,
                    suppliers.name AS supplier_name

                FROM products

                LEFT JOIN suppliers
                ON products.supplier_id = suppliers.id

                ORDER BY products.id DESC
            """).fetchall()

        return products

    # =====================================
    # 3. SEARCH PRODUCTS
    # =====================================

    def search_products(self, keyword):

        keyword = f"%{keyword.strip()}%"

        with self.db.connect() as conn:

            products = conn.execute("""
                SELECT *
                FROM products

                WHERE sku LIKE ?
                OR name LIKE ?
                OR category LIKE ?

                ORDER BY name
            """, (
                keyword,
                keyword,
                keyword
            )).fetchall()

        return products

    # =====================================
    # 4. GET PRODUCT BY ID
    # =====================================

    def get_product(self, product_id):

        with self.db.connect() as conn:

            product = conn.execute("""
                SELECT *
                FROM products
                WHERE id = ?
            """, (product_id,)).fetchone()

        return product

    # =====================================
    # 5. UPDATE PRODUCT DETAILS
    # =====================================

    def update_product(self, product_id, sku, name,
                       category, supplier_id, reorder_level,
                       unit_cost, selling_price, description=""):

        if not sku.strip() or not name.strip():
            raise ValueError("SKU and name are required.")

        if reorder_level < 0:
            raise ValueError("Reorder level cannot be negative.")

        if unit_cost < 0 or selling_price < 0:
            raise ValueError("Prices cannot be negative.")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.db.connect() as conn:

            cursor = conn.execute("""
                UPDATE products

                SET
                    sku = ?,
                    name = ?,
                    category = ?,
                    supplier_id = ?,
                    reorder_level = ?,
                    unit_cost = ?,
                    selling_price = ?,
                    description = ?,
                    updated_at = ?

                WHERE id = ?
            """, (
                sku.strip(),
                name.strip(),
                category,
                supplier_id,
                reorder_level,
                unit_cost,
                selling_price,
                description,
                now,
                product_id
            ))

            if cursor.rowcount == 0:
                raise ValueError("Product not found.")

        print("Product updated successfully!")

    # =====================================
    # 6. DELETE PRODUCT
    # =====================================

    def delete_product(self, product_id):

        with self.db.connect() as conn:

            cursor = conn.execute("""
                DELETE FROM products
                WHERE id = ?
            """, (product_id,))

            if cursor.rowcount == 0:
                raise ValueError("Product not found.")

        print("Product deleted successfully!")

    # =====================================
    # 7. STOCK IN
    # =====================================

    def stock_in(self, product_id, quantity, note=""):

        self.update_stock(
            product_id,
            "STOCK IN",
            quantity,
            note
        )

    # =====================================
    # 8. STOCK OUT
    # =====================================

    def stock_out(self, product_id, quantity, note=""):

        self.update_stock(
            product_id,
            "STOCK OUT",
            quantity,
            note
        )

    # =====================================
    # 9. UPDATE STOCK
    # =====================================

    def update_stock(self, product_id, transaction_type,
                     quantity, note=""):

        if transaction_type not in ("STOCK IN", "STOCK OUT"):
            raise ValueError("Invalid transaction type.")

        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.db.connect() as conn:

            product = conn.execute("""
                SELECT quantity
                FROM products
                WHERE id = ?
            """, (product_id,)).fetchone()

            if product is None:
                raise ValueError("Product not found.")

            current_quantity = product["quantity"]

            if transaction_type == "STOCK IN":

                new_quantity = current_quantity + quantity

            else:

                if quantity > current_quantity:
                    raise ValueError(
                        f"Insufficient stock! Available: {current_quantity}"
                    )

                new_quantity = current_quantity - quantity

            conn.execute("""
                UPDATE products

                SET quantity = ?,
                    updated_at = ?

                WHERE id = ?
            """, (
                new_quantity,
                now,
                product_id
            ))

            conn.execute("""
                INSERT INTO transactions
                (
                    product_id,
                    transaction_type,
                    quantity,
                    note,
                    transaction_date
                )

                VALUES (?, ?, ?, ?, ?)
            """, (
                product_id,
                transaction_type,
                quantity,
                note,
                now
            ))

        print("Stock updated successfully!")

    # =====================================
    # 10. LOW STOCK PRODUCTS
    # =====================================

    def get_low_stock_products(self):

        with self.db.connect() as conn:

            products = conn.execute("""
                SELECT *

                FROM products

                WHERE quantity <= reorder_level

                ORDER BY quantity ASC
            """).fetchall()

        return products

    # =====================================
    # 11. OUT OF STOCK PRODUCTS
    # =====================================

    def get_out_of_stock_products(self):

        with self.db.connect() as conn:

            products = conn.execute("""
                SELECT *

                FROM products

                WHERE quantity = 0

                ORDER BY name
            """).fetchall()

        return products

    # =====================================
    # 12. SUPPLIER MANAGEMENT
    # =====================================

    def add_supplier(self, name, contact="", email="", phone=""):

        if not name.strip():
            raise ValueError("Supplier name is required.")

        with self.db.connect() as conn:

            cursor = conn.execute("""
                INSERT INTO suppliers
                (name, contact, email, phone)

                VALUES (?, ?, ?, ?)
            """, (
                name.strip(),
                contact,
                email,
                phone
            ))

            supplier_id = cursor.lastrowid

        print("Supplier added successfully!")

        return supplier_id

    # =====================================
    # 13. DISPLAY SUPPLIERS
    # =====================================

    def get_all_suppliers(self):

        with self.db.connect() as conn:

            suppliers = conn.execute("""
                SELECT *
                FROM suppliers
                ORDER BY name
            """).fetchall()

        return suppliers

    # =====================================
    # 14. INVENTORY VALUE
    # =====================================

    def calculate_inventory_value(self):

        with self.db.connect() as conn:

            result = conn.execute("""
                SELECT
                    SUM(quantity * unit_cost) AS total_value

                FROM products
            """).fetchone()

        return result["total_value"] or 0

    # =====================================
    # 15. STOCK MOVEMENT HISTORY
    # =====================================

    def get_transaction_history(self):

        with self.db.connect() as conn:

            history = conn.execute("""
                SELECT

                    transactions.id,
                    products.sku,
                    products.name,
                    transactions.transaction_type,
                    transactions.quantity,
                    transactions.note,
                    transactions.transaction_date

                FROM transactions

                INNER JOIN products

                ON transactions.product_id = products.id

                ORDER BY transactions.id DESC
            """).fetchall()

        return history


import sqlite3
from pathlib import Path
from contextlib import contextmanager


# Project directory
BASE_DIR = Path(__file__).resolve().parent

# Database location
DB_FOLDER = BASE_DIR / "database"
DB_FOLDER.mkdir(exist_ok=True)

DB_PATH = DB_FOLDER / "inventory.db"


class Database:

    def __init__(self):
        self.create_tables()

    # Connect to database
    @contextmanager
    def connect(self):

        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row

        try:
            connection.execute("PRAGMA foreign_keys = ON")
            yield connection
            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    # Create all required tables
    def create_tables(self):

        with self.connect() as conn:

            # Products table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS products (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    sku TEXT UNIQUE NOT NULL,

                    name TEXT NOT NULL,

                    category TEXT NOT NULL,

                    supplier_id INTEGER,

                    quantity INTEGER NOT NULL DEFAULT 0
                        CHECK(quantity >= 0),

                    reorder_level INTEGER NOT NULL DEFAULT 5
                        CHECK(reorder_level >= 0),

                    unit_cost REAL NOT NULL DEFAULT 0
                        CHECK(unit_cost >= 0),

                    selling_price REAL NOT NULL DEFAULT 0
                        CHECK(selling_price >= 0),

                    description TEXT,

                    created_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL,

                    FOREIGN KEY(supplier_id)
                    REFERENCES suppliers(id)
                    ON DELETE SET NULL
                )
            """)

            # Suppliers table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS suppliers (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    name TEXT UNIQUE NOT NULL,

                    contact TEXT,

                    email TEXT,

                    phone TEXT
                )
            """)

            # Stock transaction table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    product_id INTEGER NOT NULL,

                    transaction_type TEXT NOT NULL
                        CHECK(transaction_type IN
                        ('STOCK IN', 'STOCK OUT')),

                    quantity INTEGER NOT NULL
                        CHECK(quantity > 0),

                    note TEXT,

                    transaction_date TEXT NOT NULL,

                    FOREIGN KEY(product_id)
                    REFERENCES products(id)
                    ON DELETE RESTRICT
                )
            """)

            # Database indexes for faster searching
            conn.execute("""
                CREATE INDEX IF NOT EXISTS
                idx_product_name
                ON products(name)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS
                idx_transaction_date
                ON transactions(transaction_date)
            """)

        print("Database initialized successfully!")


# Test database connection
if __name__ == "__main__":

    db = Database()

    print("Database path:", DB_PATH)

    print("All tables created successfully!")

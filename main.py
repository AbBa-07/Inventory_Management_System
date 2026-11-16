
import tkinter as tk
from tkinter import ttk, messagebox

from inventory import InventoryManager
from reports import ReportManager
from database import Database


# ==========================================
# APPLICATION CONFIGURATION
# ==========================================

BG = "#F1F5F9"
NAVY = "#17243A"
BLUE = "#2563EB"
WHITE = "#FFFFFF"
TEXT = "#1E293B"
MUTED = "#64748B"
GREEN = "#15803D"
RED = "#DC2626"

CATEGORIES = [
    "Electronics",
    "Accessories",
    "Stationery",
    "Furniture",
    "Hardware",
    "Clothing",
    "Food",
    "Other"
]


# ==========================================
# MAIN APPLICATION
# ==========================================

class InventoryApplication(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title("Inventory Management System")
        self.geometry("1350x800")
        self.minsize(1100, 650)
        self.configure(bg=BG)

        self.inventory = InventoryManager()
        self.reports = ReportManager()
        self.database = Database()

        self.setup_styles()
        self.create_layout()
        self.show_dashboard()

    # ======================================
    # STYLING
    # ======================================

    def setup_styles(self):

        style = ttk.Style(self)

        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=WHITE,
            foreground=TEXT,
            rowheight=30,
            fieldbackground=WHITE,
            font=("Segoe UI", 9)
        )

        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#E2E8F0",
            foreground=TEXT
        )

        style.configure(
            "TButton",
            font=("Segoe UI", 9),
            padding=7
        )

        style.configure(
            "TCombobox",
            padding=6
        )

        style.configure(
            "TEntry",
            padding=6
        )

        style.map(
            "Treeview",
            background=[("selected", "#BFDBFE")],
            foreground=[("selected", TEXT)]
        )

    # ======================================
    # MAIN LAYOUT
    # ======================================

    def create_layout(self):

        # Sidebar
        self.sidebar = tk.Frame(
            self,
            bg=NAVY,
            width=225
        )

        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Main content
        self.content = tk.Frame(
            self,
            bg=BG
        )

        self.content.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.create_sidebar()

    # ======================================
    # SIDEBAR
    # ======================================

    def create_sidebar(self):

        tk.Label(
            self.sidebar,
            text="IMS",
            font=("Segoe UI", 27, "bold"),
            bg=NAVY,
            fg=WHITE
        ).pack(pady=(30, 2))

        tk.Label(
            self.sidebar,
            text="INVENTORY SYSTEM",
            font=("Segoe UI", 9, "bold"),
            bg=NAVY,
            fg="#94A3B8"
        ).pack(pady=(0, 35))

        navigation = [
            ("Dashboard", self.show_dashboard),
            ("Products", self.show_products),
            ("Stock Management", self.show_stock),
            ("Suppliers", self.show_suppliers),
            ("Reports & Analytics", self.show_reports)
        ]

        for title, command in navigation:

            button = tk.Button(
                self.sidebar,
                text=title,
                command=command,
                bg=NAVY,
                fg=WHITE,
                activebackground=BLUE,
                activeforeground=WHITE,
                relief="flat",
                anchor="w",
                padx=25,
                pady=13,
                font=("Segoe UI", 10)
            )

            button.pack(fill="x", padx=10, pady=3)

        tk.Label(
            self.sidebar,
            text="Python | SQLite | Tkinter",
            font=("Segoe UI", 8),
            bg=NAVY,
            fg="#94A3B8"
        ).pack(side="bottom", pady=20)

    # ======================================
    # CLEAR MAIN CONTENT
    # ======================================

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    # ======================================
    # PAGE HEADER
    # ======================================

    def page_header(self, title, subtitle):

        tk.Label(
            self.content,
            text=title,
            font=("Segoe UI", 23, "bold"),
            bg=BG,
            fg=TEXT
        ).pack(anchor="w", padx=30, pady=(22, 2))

        tk.Label(
            self.content,
            text=subtitle,
            font=("Segoe UI", 10),
            bg=BG,
            fg=MUTED
        ).pack(anchor="w", padx=30, pady=(0, 18))

    # ======================================
    # DASHBOARD
    # ======================================

    def show_dashboard(self):

        self.clear_content()

        self.page_header(
            "Dashboard",
            "Overview of your inventory and business operations."
        )

        stats = self.reports.inventory_summary()

        card_frame = tk.Frame(
            self.content,
            bg=BG
        )

        card_frame.pack(fill="x", padx=20)

        cards = [
            ("Total Products", stats["total_products"], BLUE),
            ("Total Units", stats["total_units"], GREEN),
            (
                "Inventory Value",
                f"₹{stats['total_cost_value']:,.2f}",
                "#7C3AED"
            ),
            ("Low Stock", stats["low_stock_count"], "#D97706"),
            ("Out of Stock", stats["out_of_stock_count"], RED)
        ]

        for title, value, color in cards:

            card = tk.Frame(
                card_frame,
                bg=WHITE,
                highlightbackground="#E2E8F0",
                highlightthickness=1
            )

            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=7,
                pady=8
            )

            tk.Label(
                card,
                text=title.upper(),
                bg=WHITE,
                fg=MUTED,
                font=("Segoe UI", 8, "bold")
            ).pack(anchor="w", padx=12, pady=(15, 5))

            tk.Label(
                card,
                text=value,
                bg=WHITE,
                fg=color,
                font=("Segoe UI", 18, "bold")
            ).pack(anchor="w", padx=12, pady=(0, 15))

        # Low stock table
        tk.Label(
            self.content,
            text="LOW STOCK ALERTS",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=30, pady=(25, 10))

        columns = (
            "SKU",
            "Product",
            "Category",
            "Available",
            "Reorder Level"
        )

        tree = ttk.Treeview(
            self.content,
            columns=columns,
            show="headings",
            height=9
        )

        for col in columns:

            tree.heading(col, text=col)
            tree.column(col, width=150)

        tree.pack(fill="x", padx=30)

        for item in self.inventory.get_low_stock_products():

            tree.insert(
                "",
                "end",
                values=(
                    item["sku"],
                    item["name"],
                    item["category"],
                    item["quantity"],
                    item["reorder_level"]
                )
            )

        ttk.Button(
            self.content,
            text="Refresh Dashboard",
            command=self.show_dashboard
        ).pack(anchor="e", padx=30, pady=15)

    # ======================================
    # PRODUCT MANAGEMENT
    # ======================================

    def show_products(self):

        self.clear_content()

        self.page_header(
            "Product Management",
            "Add, update, search and manage inventory products."
        )

        toolbar = tk.Frame(self.content, bg=BG)
        toolbar.pack(fill="x", padx=30, pady=5)

        self.search_var = tk.StringVar()
        self.category_filter_var = tk.StringVar(value="All Categories")
        self.stock_filter_var = tk.StringVar(value="All Stock")
        self.sort_filter_var = tk.StringVar(value="Default")

        ttk.Entry(
            toolbar,
            textvariable=self.search_var,
            width=24
        ).pack(side="left", padx=5)

        ttk.Button(
            toolbar,
            text="Search",
            command=self.apply_product_filters
        ).pack(side="left", padx=5)

        ttk.Label(toolbar, text="Category:", background=BG).pack(side="left", padx=(10, 3))
        self.category_filter = ttk.Combobox(
            toolbar,
            textvariable=self.category_filter_var,
            values=["All Categories"] + CATEGORIES,
            state="readonly",
            width=16
        )
        self.category_filter.pack(side="left", padx=4)
        self.category_filter.bind("<<ComboboxSelected>>", lambda event: self.apply_product_filters())

        ttk.Label(toolbar, text="Stock:", background=BG).pack(side="left", padx=(8, 3))
        self.stock_filter = ttk.Combobox(
            toolbar,
            textvariable=self.stock_filter_var,
            values=["All Stock", "In Stock", "Low Stock", "Out of Stock"],
            state="readonly",
            width=13
        )
        self.stock_filter.pack(side="left", padx=4)
        self.stock_filter.bind("<<ComboboxSelected>>", lambda event: self.apply_product_filters())

        ttk.Label(toolbar, text="Sort:", background=BG).pack(side="left", padx=(8, 3))
        self.sort_filter = ttk.Combobox(
            toolbar,
            textvariable=self.sort_filter_var,
            values=[
                "Default",
                "Quantity: Low to High",
                "Quantity: High to Low",
                "Value: Low to High",
                "Value: High to Low"
            ],
            state="readonly",
            width=19
        )
        self.sort_filter.pack(side="left", padx=4)
        self.sort_filter.bind("<<ComboboxSelected>>", lambda event: self.apply_product_filters())

        ttk.Button(
            toolbar,
            text="Reset Filters",
            command=self.reset_product_filters
        ).pack(side="left", padx=5)

        ttk.Button(
            toolbar,
            text="+ Add Product",
            command=self.add_product_window
        ).pack(side="right", padx=5)

        ttk.Button(
            toolbar,
            text="Edit Selected",
            command=self.edit_product
        ).pack(side="right", padx=5)

        ttk.Button(
            toolbar,
            text="Delete Selected",
            command=self.delete_product
        ).pack(side="right", padx=5)

        columns = (
            "ID", "SKU", "Name", "Category",
            "Quantity", "Reorder", "Cost", "Price", "Status"
        )

        self.product_tree = ttk.Treeview(
            self.content,
            columns=columns,
            show="headings"
        )

        for col in columns:

            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=115)

        # Visually distinguish stock conditions.
        self.product_tree.tag_configure(
            "out_of_stock",
            background="#FEE2E2",
            foreground="#991B1B"
        )
        self.product_tree.tag_configure(
            "low_stock",
            background="#FEF3C7",
            foreground="#92400E"
        )
        self.product_tree.tag_configure(
            "in_stock",
            background="#DCFCE7",
            foreground="#166534"
        )

        self.product_tree.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=15
        )

        self.refresh_product_table()

    def refresh_product_table(self):

        self.apply_product_filters()

    def apply_product_filters(self):

        self.product_tree.delete(*self.product_tree.get_children())
        products = self.inventory.get_all_products()

        keyword = self.search_var.get().strip().lower()
        if keyword:
            products = [
                p for p in products
                if keyword in str(p["name"]).lower()
                or keyword in str(p["sku"]).lower()
            ]

        selected_category = self.category_filter_var.get()
        if selected_category != "All Categories":
            products = [p for p in products if p["category"] == selected_category]

        selected_stock = self.stock_filter_var.get()
        if selected_stock == "Out of Stock":
            products = [p for p in products if p["quantity"] == 0]
        elif selected_stock == "Low Stock":
            products = [
                p for p in products
                if 0 < p["quantity"] <= p["reorder_level"]
            ]
        elif selected_stock == "In Stock":
            products = [p for p in products if p["quantity"] > p["reorder_level"]]

        sort_option = self.sort_filter_var.get()
        if sort_option == "Quantity: Low to High":
            products.sort(key=lambda p: p["quantity"])
        elif sort_option == "Quantity: High to Low":
            products.sort(key=lambda p: p["quantity"], reverse=True)
        elif sort_option == "Value: Low to High":
            products.sort(key=lambda p: p["quantity"] * p["unit_cost"])
        elif sort_option == "Value: High to Low":
            products.sort(
                key=lambda p: p["quantity"] * p["unit_cost"],
                reverse=True
            )

        for p in products:

            if p["quantity"] == 0:
                status = "Out of Stock"
                row_tag = "out_of_stock"
            elif p["quantity"] <= p["reorder_level"]:
                status = "Low Stock"
                row_tag = "low_stock"
            else:
                status = "In Stock"
                row_tag = "in_stock"

            self.product_tree.insert(
                "",
                "end",
                values=(
                    p["id"], p["sku"], p["name"], p["category"],
                    p["quantity"], p["reorder_level"],
                    f"₹{p['unit_cost']:,.2f}",
                    f"₹{p['selling_price']:,.2f}",
                    status
                ),
                tags=(row_tag,)
            )

    def search_products(self):
        self.apply_product_filters()

    def reset_product_filters(self):
        self.search_var.set("")
        self.category_filter_var.set("All Categories")
        self.stock_filter_var.set("All Stock")
        self.sort_filter_var.set("Default")
        self.apply_product_filters()

    # ADD / EDIT PRODUCT WINDOW
    # ======================================

    def add_product_window(self, product=None):

        editing = product is not None

        window = tk.Toplevel(self)

        window.title(
            "Edit Product" if editing else "Add Product"
        )

        window.geometry("480x610")
        window.configure(bg=BG)
        window.transient(self)
        window.grab_set()

        tk.Label(
            window,
            text="Edit Product" if editing else "Add New Product",
            font=("Segoe UI", 19, "bold"),
            bg=BG,
            fg=TEXT
        ).pack(pady=15)

        suppliers = self.inventory.get_all_suppliers()

        supplier_options = {
            s["name"]: s["id"] for s in suppliers
        }

        supplier_names = ["None"] + list(supplier_options.keys())

        fields = [
            ("SKU", "sku"),
            ("Product Name", "name"),
            ("Category", "category"),
            ("Supplier", "supplier"),
            ("Quantity", "quantity"),
            ("Reorder Level", "reorder"),
            ("Unit Cost", "cost"),
            ("Selling Price", "price"),
            ("Description", "description")
        ]

        entries = {}

        form = tk.Frame(window, bg=BG)
        form.pack(padx=30, fill="x")

        for index, (label, key) in enumerate(fields):

            tk.Label(
                form,
                text=label,
                bg=BG,
                fg=TEXT,
                font=("Segoe UI", 9, "bold")
            ).grid(
                row=index,
                column=0,
                sticky="w",
                pady=7
            )

            initial = ""

            if editing:

                mapping = {
                    "sku": product["sku"],
                    "name": product["name"],
                    "category": product["category"],
                    "quantity": product["quantity"],
                    "reorder": product["reorder_level"],
                    "cost": product["unit_cost"],
                    "price": product["selling_price"],
                    "description": product["description"] or ""
                }

                initial = str(mapping.get(key, ""))

                if key == "supplier":

                    initial = next(
                        (
                            name for name, sid in supplier_options.items()
                            if sid == product["supplier_id"]
                        ),
                        "None"
                    )

            if key == "category":

                widget = ttk.Combobox(
                    form,
                    values=CATEGORIES,
                    state="readonly",
                    width=27
                )

                widget.set(initial or CATEGORIES[0])

            elif key == "supplier":

                widget = ttk.Combobox(
                    form,
                    values=supplier_names,
                    state="readonly",
                    width=27
                )

                widget.set(initial or "None")

            else:

                widget = ttk.Entry(form, width=30)
                widget.insert(0, initial)

                if editing and key == "quantity":
                    widget.configure(state="disabled")

            widget.grid(
                row=index,
                column=1,
                pady=5,
                padx=10
            )

            entries[key] = widget

        def save_product():

            try:

                sku = entries["sku"].get().strip()
                name = entries["name"].get().strip()
                category = entries["category"].get()
                supplier_name = entries["supplier"].get()

                supplier_id = supplier_options.get(supplier_name)

                quantity = (
                    0 if editing
                    else int(entries["quantity"].get())
                )

                reorder = int(entries["reorder"].get())
                cost = float(entries["cost"].get())
                price = float(entries["price"].get())

                description = entries["description"].get().strip()

                if editing:

                    self.inventory.update_product(
                        product["id"],
                        sku,
                        name,
                        category,
                        supplier_id,
                        reorder,
                        cost,
                        price,
                        description
                    )

                else:

                    self.inventory.add_product(
                        sku,
                        name,
                        category,
                        supplier_id,
                        quantity,
                        reorder,
                        cost,
                        price,
                        description
                    )

                window.destroy()

                self.refresh_product_table()
                self.show_dashboard()

                messagebox.showinfo(
                    "Success",
                    "Product saved successfully!"
                )

            except ValueError as error:

                messagebox.showerror(
                    "Invalid Input",
                    str(error)
                )

            except Exception as error:

                messagebox.showerror(
                    "Error",
                    str(error)
                )

        ttk.Button(
            window,
            text="Save Product",
            command=save_product
        ).pack(pady=20)

    def get_selected_product(self):

        selected = self.product_tree.selection()

        if not selected:

            messagebox.showwarning(
                "Selection Required",
                "Please select a product."
            )

            return None

        values = self.product_tree.item(
            selected[0],
            "values"
        )

        return self.inventory.get_product(int(values[0]))

    def edit_product(self):

        product = self.get_selected_product()

        if product:

            self.add_product_window(product)

    def delete_product(self):

        product = self.get_selected_product()

        if not product:
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to delete this product?"
        )

        if confirm:

            try:

                self.inventory.delete_product(product["id"])

                self.refresh_product_table()
                self.show_dashboard()

                messagebox.showinfo(
                    "Success",
                    "Product deleted successfully!"
                )

            except Exception as error:

                messagebox.showerror(
                    "Cannot Delete",
                    str(error)
                )

    # ======================================
    # STOCK MANAGEMENT
    # ======================================

    def show_stock(self):

        self.clear_content()

        self.page_header(
            "Stock Management",
            "Record incoming and outgoing stock movements."
        )

        form = tk.LabelFrame(
            self.content,
            text="New Stock Transaction",
            bg=BG,
            padx=15,
            pady=15
        )

        form.pack(fill="x", padx=30, pady=10)

        products = self.inventory.get_all_products()

        product_map = {
            f"{p['id']} | {p['sku']} | {p['name']}": p["id"]
            for p in products
        }

        self.stock_product = ttk.Combobox(
            form,
            values=list(product_map.keys()),
            state="readonly",
            width=35
        )

        self.stock_product.grid(row=1, column=0, padx=8, pady=8)

        self.stock_type = ttk.Combobox(
            form,
            values=["STOCK IN", "STOCK OUT"],
            state="readonly",
            width=15
        )

        self.stock_type.set("STOCK IN")
        self.stock_type.grid(row=1, column=1, padx=8)

        self.stock_quantity = ttk.Entry(form, width=15)
        self.stock_quantity.grid(row=1, column=2, padx=8)

        self.stock_note = ttk.Entry(form, width=25)
        self.stock_note.grid(row=1, column=3, padx=8)

        labels = [
            "Product",
            "Transaction",
            "Quantity",
            "Note"
        ]

        for i, label in enumerate(labels):

            tk.Label(
                form,
                text=label,
                bg=BG
            ).grid(row=0, column=i, sticky="w", padx=8)

        ttk.Button(
            form,
            text="Save Transaction",
            command=lambda: self.save_stock_transaction(product_map)
        ).grid(row=1, column=4, padx=8)

        tk.Label(
            self.content,
            text="TRANSACTION HISTORY",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=30, pady=(15, 5))

        history_filters = tk.Frame(self.content, bg=BG)
        history_filters.pack(fill="x", padx=30, pady=5)

        self.transaction_search_var = tk.StringVar()
        self.transaction_type_filter_var = tk.StringVar(value="All Types")

        ttk.Entry(
            history_filters,
            textvariable=self.transaction_search_var,
            width=30
        ).pack(side="left", padx=5)

        ttk.Label(
            history_filters,
            text="Transaction:",
            background=BG
        ).pack(side="left", padx=(10, 3))

        transaction_filter = ttk.Combobox(
            history_filters,
            textvariable=self.transaction_type_filter_var,
            values=["All Types", "STOCK IN", "STOCK OUT"],
            state="readonly",
            width=14
        )
        transaction_filter.pack(side="left", padx=5)
        transaction_filter.bind(
            "<<ComboboxSelected>>",
            lambda event: self.refresh_transactions()
        )

        ttk.Button(
            history_filters,
            text="Search History",
            command=self.refresh_transactions
        ).pack(side="left", padx=5)

        ttk.Button(
            history_filters,
            text="Reset",
            command=self.reset_transaction_filters
        ).pack(side="left", padx=5)

        columns = (
            "ID", "Date", "SKU", "Product",
            "Type", "Quantity", "Note"
        )

        self.transaction_tree = ttk.Treeview(
            self.content,
            columns=columns,
            show="headings"
        )

        for col in columns:

            self.transaction_tree.heading(col, text=col)
            self.transaction_tree.column(col, width=130)

        self.transaction_tree.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        self.refresh_transactions()

    def save_stock_transaction(self, product_map):

        try:

            product_label = self.stock_product.get()

            if product_label not in product_map:
                raise ValueError("Please select a product.")

            product_id = product_map[product_label]

            quantity = int(self.stock_quantity.get())

            kind = self.stock_type.get()

            note = self.stock_note.get().strip()

            if kind == "STOCK IN":

                self.inventory.stock_in(
                    product_id,
                    quantity,
                    note
                )

            else:

                self.inventory.stock_out(
                    product_id,
                    quantity,
                    note
                )

            messagebox.showinfo(
                "Success",
                "Stock transaction recorded!"
            )

            self.show_stock()

        except Exception as error:

            messagebox.showerror(
                "Transaction Failed",
                str(error)
            )

    def refresh_transactions(self):

        self.transaction_tree.delete(
            *self.transaction_tree.get_children()
        )

        history = self.inventory.get_transaction_history()

        keyword = self.transaction_search_var.get().strip().lower()
        selected_type = self.transaction_type_filter_var.get()

        if selected_type != "All Types":
            history = [
                row for row in history
                if row["transaction_type"] == selected_type
            ]

        if keyword:
            history = [
                row for row in history
                if keyword in str(row["sku"]).lower()
                or keyword in str(row["name"]).lower()
                or keyword in str(row["note"] or "").lower()
                or keyword in str(row["transaction_date"]).lower()
            ]

        for row in history:

            self.transaction_tree.insert(
                "",
                "end",
                values=(
                    row["id"],
                    row["transaction_date"],
                    row["sku"],
                    row["name"],
                    row["transaction_type"],
                    row["quantity"],
                    row["note"]
                )
            )

    def reset_transaction_filters(self):

        self.transaction_search_var.set("")
        self.transaction_type_filter_var.set("All Types")
        self.refresh_transactions()

    # ======================================
    # SUPPLIER MANAGEMENT
    # ======================================

    def show_suppliers(self):

        self.clear_content()

        self.page_header(
            "Supplier Management",
            "Maintain supplier information and contact details."
        )

        form = tk.LabelFrame(
            self.content,
            text="Add New Supplier",
            bg=BG,
            padx=15,
            pady=15
        )

        form.pack(fill="x", padx=30, pady=10)

        self.supplier_name = ttk.Entry(form, width=25)
        self.supplier_contact = ttk.Entry(form, width=25)
        self.supplier_email = ttk.Entry(form, width=25)
        self.supplier_phone = ttk.Entry(form, width=20)

        fields = [
            ("Supplier Name", self.supplier_name),
            ("Contact Person", self.supplier_contact),
            ("Email", self.supplier_email),
            ("Phone", self.supplier_phone)
        ]

        for i, (label, entry) in enumerate(fields):

            tk.Label(
                form,
                text=label,
                bg=BG
            ).grid(row=0, column=i, sticky="w", padx=5)

            entry.grid(
                row=1,
                column=i,
                padx=5,
                pady=8
            )

        ttk.Button(
            form,
            text="Add Supplier",
            command=self.add_supplier
        ).grid(row=1, column=4, padx=10)

        columns = (
            "ID",
            "Name",
            "Contact",
            "Email",
            "Phone"
        )

        self.supplier_tree = ttk.Treeview(
            self.content,
            columns=columns,
            show="headings"
        )

        for col in columns:

            self.supplier_tree.heading(col, text=col)
            self.supplier_tree.column(col, width=160)

        self.supplier_tree.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        self.refresh_suppliers()

    def add_supplier(self):

        try:

            self.inventory.add_supplier(
                self.supplier_name.get(),
                self.supplier_contact.get(),
                self.supplier_email.get(),
                self.supplier_phone.get()
            )

            self.show_suppliers()

            messagebox.showinfo(
                "Success",
                "Supplier added successfully!"
            )

        except Exception as error:

            messagebox.showerror(
                "Error",
                str(error)
            )

    def refresh_suppliers(self):

        self.supplier_tree.delete(
            *self.supplier_tree.get_children()
        )

        for supplier in self.inventory.get_all_suppliers():

            self.supplier_tree.insert(
                "",
                "end",
                values=(
                    supplier["id"],
                    supplier["name"],
                    supplier["contact"],
                    supplier["email"],
                    supplier["phone"]
                )
            )

    # ======================================
    # REPORTS AND ANALYTICS
    # ======================================

    def show_reports(self):

        self.clear_content()

        self.page_header(
            "Reports & Analytics",
            "Financial analysis and inventory performance."
        )

        summary = self.reports.inventory_summary()

        summary_frame = tk.LabelFrame(
            self.content,
            text="Inventory Summary",
            bg=BG,
            padx=20,
            pady=15
        )

        summary_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )

        report_text = (
            f"Total Products: {summary['total_products']}\n"
            f"Total Units: {summary['total_units']}\n"
            f"Inventory Cost Value: ₹{summary['total_cost_value']:,.2f}\n"
            f"Potential Sales Value: ₹{summary['potential_sales_value']:,.2f}\n"
            f"Low Stock Products: {summary['low_stock_count']}\n"
            f"Out of Stock Products: {summary['out_of_stock_count']}"
        )

        tk.Label(
            summary_frame,
            text=report_text,
            bg=BG,
            fg=TEXT,
            justify="left",
            font=("Segoe UI", 11)
        ).pack(anchor="w")

        # Export buttons
        button_frame = tk.Frame(
            self.content,
            bg=BG
        )

        button_frame.pack(
            fill="x",
            padx=30,
            pady=15
        )

        ttk.Button(
            button_frame,
            text="Export Inventory CSV",
            command=self.export_inventory
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Export Transactions CSV",
            command=self.export_transactions
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Export Inventory Excel",
            command=self.export_inventory_excel
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Export Inventory PDF",
            command=self.export_inventory_pdf
        ).pack(side="left", padx=5)

        # Charts
        chart_frame = tk.LabelFrame(
            self.content,
            text="Data Visualization",
            bg=BG,
            padx=15,
            pady=15
        )

        chart_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )

        ttk.Button(
            chart_frame,
            text="Category Valuation Chart",
            command=self.category_chart
        ).pack(side="left", padx=8)

        ttk.Button(
            chart_frame,
            text="Stock Distribution Chart",
            command=self.stock_chart
        ).pack(side="left", padx=8)

        ttk.Button(
            chart_frame,
            text="Stock Movement Chart",
            command=self.movement_chart
        ).pack(side="left", padx=8)

        ttk.Button(
            chart_frame,
            text="Refresh Reports",
            command=self.show_reports
        ).pack(side="right", padx=8)

        # Category summary table
        tk.Label(
            self.content,
            text="CATEGORY-WISE ANALYSIS",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=30, pady=10)

        columns = (
            "Category",
            "Products",
            "Units",
            "Value"
        )

        self.category_tree = ttk.Treeview(
            self.content,
            columns=columns,
            show="headings",
            height=8
        )

        for col in columns:

            self.category_tree.heading(col, text=col)
            self.category_tree.column(col, width=160)

        self.category_tree.pack(
            fill="x",
            padx=30,
            pady=5
        )

        for item in self.reports.category_analysis():

            self.category_tree.insert(
                "",
                "end",
                values=(
                    item["category"],
                    item["product_count"],
                    item["total_units"],
                    f"₹{item['inventory_value'] or 0:,.2f}"
                )
            )

    # ======================================
    # CHART FUNCTIONS
    # ======================================

    def category_chart(self):

        try:

            self.reports.generate_category_chart()

        except Exception as error:

            messagebox.showerror("Chart Error", str(error))

    def stock_chart(self):

        try:

            self.reports.generate_stock_chart()

        except Exception as error:

            messagebox.showerror("Chart Error", str(error))

    def movement_chart(self):

        try:

            self.reports.generate_movement_chart()

        except Exception as error:

            messagebox.showerror("Chart Error", str(error))

    # ======================================
    # CSV EXPORT
    # ======================================

    def export_inventory(self):

        try:

            filepath = self.reports.export_inventory_csv()

            messagebox.showinfo(
                "Export Successful",
                f"Inventory report saved at:\n{filepath}"
            )

        except Exception as error:

            messagebox.showerror("Export Error", str(error))

    def export_transactions(self):

        try:

            filepath = self.reports.export_transaction_csv()

            messagebox.showinfo(
                "Export Successful",
                f"Transaction report saved at:\n{filepath}"
            )

        except Exception as error:

            messagebox.showerror("Export Error", str(error))

    def export_inventory_excel(self):

        try:

            filepath = self.reports.export_inventory_excel()

            messagebox.showinfo(
                "Export Successful",
                f"Excel inventory report saved at:\n{filepath}"
            )

        except Exception as error:

            messagebox.showerror("Excel Export Error", str(error))

    def export_inventory_pdf(self):

        try:

            filepath = self.reports.export_inventory_pdf()

            messagebox.showinfo(
                "Export Successful",
                f"PDF inventory report saved at:\n{filepath}"
            )

        except Exception as error:

            messagebox.showerror("PDF Export Error", str(error))


# ==========================================
# START APPLICATION
# ==========================================

if __name__ == "__main__":

    app = InventoryApplication()

    app.mainloop()

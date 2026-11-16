
import csv
from pathlib import Path
from datetime import datetime

from database import Database
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


BASE_DIR = Path(__file__).resolve().parent

EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(exist_ok=True)


class ReportManager:

    def __init__(self):
        self.db = Database()

    # =========================================
    # 1. GENERAL INVENTORY SUMMARY
    # =========================================

    def inventory_summary(self):

        with self.db.connect() as conn:

            result = conn.execute("""
                SELECT

                    COUNT(*) AS total_products,

                    COALESCE(SUM(quantity), 0) AS total_units,

                    COALESCE(
                        SUM(quantity * unit_cost), 0
                    ) AS total_cost_value,

                    COALESCE(
                        SUM(quantity * selling_price), 0
                    ) AS potential_sales_value,

                    COALESCE(
                        SUM(CASE
                            WHEN quantity <= reorder_level
                            THEN 1 ELSE 0
                        END), 0
                    ) AS low_stock_count,

                    COALESCE(
                        SUM(CASE
                            WHEN quantity = 0
                            THEN 1 ELSE 0
                        END), 0
                    ) AS out_of_stock_count

                FROM products
            """).fetchone()

        return dict(result)

    # =========================================
    # 2. CATEGORY-WISE ANALYSIS
    # =========================================

    def category_analysis(self):

        with self.db.connect() as conn:

            result = conn.execute("""
                SELECT

                    category,

                    COUNT(*) AS product_count,

                    SUM(quantity) AS total_units,

                    SUM(quantity * unit_cost) AS inventory_value

                FROM products

                GROUP BY category

                ORDER BY inventory_value DESC
            """).fetchall()

        return [dict(row) for row in result]

    # =========================================
    # 3. LOW STOCK ANALYSIS
    # =========================================

    def low_stock_analysis(self):

        with self.db.connect() as conn:

            result = conn.execute("""
                SELECT

                    sku,
                    name,
                    category,
                    quantity,
                    reorder_level,

                    (reorder_level - quantity)
                    AS shortage

                FROM products

                WHERE quantity <= reorder_level

                ORDER BY quantity ASC
            """).fetchall()

        return [dict(row) for row in result]

    # =========================================
    # 4. REORDER RECOMMENDATION
    # =========================================

    def reorder_recommendations(self):

        with self.db.connect() as conn:

            result = conn.execute("""
                SELECT

                    sku,
                    name,
                    quantity,
                    reorder_level,

                    CASE
                        WHEN quantity = 0
                        THEN reorder_level + 10

                        WHEN quantity <= reorder_level
                        THEN (reorder_level * 2) - quantity

                        ELSE 0
                    END AS suggested_order

                FROM products

                WHERE quantity <= reorder_level

                ORDER BY suggested_order DESC
            """).fetchall()

        return [dict(row) for row in result]

    # =========================================
    # 5. THRESHOLD COMPARISON
    # =========================================

    def compare_thresholds(self, threshold_1, threshold_2):

        if threshold_1 < 0 or threshold_2 < 0:
            raise ValueError("Thresholds cannot be negative.")

        with self.db.connect() as conn:

            result = conn.execute("""
                SELECT

                    COUNT(*) AS total_products,

                    SUM(CASE
                        WHEN quantity <= ?
                        THEN 1 ELSE 0
                    END) AS threshold_1_count,

                    SUM(CASE
                        WHEN quantity <= ?
                        THEN 1 ELSE 0
                    END) AS threshold_2_count

                FROM products
            """, (threshold_1, threshold_2)).fetchone()

        return {
            "threshold_1": threshold_1,
            "threshold_2": threshold_2,
            "threshold_1_count": result["threshold_1_count"] or 0,
            "threshold_2_count": result["threshold_2_count"] or 0,
            "total_products": result["total_products"]
        }

    # =========================================
    # 6. STOCK MOVEMENT ANALYSIS
    # =========================================

    def stock_movement_analysis(self):

        with self.db.connect() as conn:

            result = conn.execute("""
                SELECT

                    transaction_type,

                    COUNT(*) AS transaction_count,

                    SUM(quantity) AS total_quantity

                FROM transactions

                GROUP BY transaction_type
            """).fetchall()

        return [dict(row) for row in result]

    # =========================================
    # 7. PRODUCT PROFIT MARGIN ANALYSIS
    # =========================================

    def profit_margin_analysis(self):

        with self.db.connect() as conn:

            result = conn.execute("""
                SELECT

                    sku,
                    name,
                    unit_cost,
                    selling_price,

                    (selling_price - unit_cost)
                    AS profit_per_unit,

                    CASE
                        WHEN selling_price > 0
                        THEN
                            ((selling_price - unit_cost)
                            / selling_price) * 100
                        ELSE 0
                    END AS profit_margin

                FROM products

                ORDER BY profit_margin DESC
            """).fetchall()

        return [dict(row) for row in result]

    # =========================================
    # 8. EXPORT INVENTORY REPORT
    # =========================================

    def export_inventory_csv(self):

        with self.db.connect() as conn:

            rows = conn.execute("""
                SELECT

                    p.sku,
                    p.name,
                    p.category,
                    s.name AS supplier,
                    p.quantity,
                    p.reorder_level,
                    p.unit_cost,
                    p.selling_price,

                    (p.quantity * p.unit_cost)
                    AS inventory_value

                FROM products p

                LEFT JOIN suppliers s
                ON p.supplier_id = s.id

                ORDER BY p.name
            """).fetchall()

        filename = (
            "inventory_report_"
            + datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".csv"
        )

        filepath = EXPORT_DIR / filename

        with open(filepath, "w", newline="", encoding="utf-8-sig") as file:

            writer = csv.writer(file)

            writer.writerow([
                "SKU",
                "Product Name",
                "Category",
                "Supplier",
                "Quantity",
                "Reorder Level",
                "Unit Cost",
                "Selling Price",
                "Inventory Value"
            ])

            for row in rows:

                writer.writerow([
                    row["sku"],
                    row["name"],
                    row["category"],
                    row["supplier"] or "",
                    row["quantity"],
                    row["reorder_level"],
                    row["unit_cost"],
                    row["selling_price"],
                    row["inventory_value"]
                ])

        return filepath

    # =========================================
    # 9. EXPORT TRANSACTION REPORT
    # =========================================

    def export_transaction_csv(self):

        with self.db.connect() as conn:

            rows = conn.execute("""
                SELECT

                    t.id,
                    p.sku,
                    p.name,
                    t.transaction_type,
                    t.quantity,
                    t.note,
                    t.transaction_date

                FROM transactions t

                INNER JOIN products p

                ON t.product_id = p.id

                ORDER BY t.transaction_date DESC
            """).fetchall()

        filename = (
            "transaction_report_"
            + datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".csv"
        )

        filepath = EXPORT_DIR / filename

        with open(filepath, "w", newline="", encoding="utf-8-sig") as file:

            writer = csv.writer(file)

            writer.writerow([
                "Transaction ID",
                "SKU",
                "Product",
                "Transaction Type",
                "Quantity",
                "Note",
                "Date"
            ])

            for row in rows:
                writer.writerow(list(row))

        return filepath

    # =========================================
    # 10. EXPORT INVENTORY REPORT TO EXCEL
    # =========================================

    def export_inventory_excel(self):

        with self.db.connect() as conn:

            products = conn.execute("""
                SELECT
                    p.sku,
                    p.name,
                    p.category,
                    s.name AS supplier,
                    p.quantity,
                    p.reorder_level,
                    p.unit_cost,
                    p.selling_price,
                    (p.quantity * p.unit_cost) AS inventory_value
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                ORDER BY p.name
            """).fetchall()

        filename = (
            "inventory_report_"
            + datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".xlsx"
        )

        filepath = EXPORT_DIR / filename

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Inventory Report"

        headers = [
            "SKU", "Product Name", "Category", "Supplier",
            "Quantity", "Reorder Level", "Unit Cost",
            "Selling Price", "Inventory Value"
        ]
        sheet.append(headers)

        # Format the heading row.
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(
                start_color="1F4E78",
                end_color="1F4E78",
                fill_type="solid"
            )
            cell.alignment = Alignment(horizontal="center")

        # Add the inventory records.
        for product in products:
            sheet.append(list(product))

        # Adjust column widths to fit their contents.
        for column in sheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)

            for cell in column:
                if cell.value is not None:
                    max_length = max(max_length, len(str(cell.value)))

            sheet.column_dimensions[column_letter].width = max_length + 4

        # Keep headings visible and enable column filters.
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions

        workbook.save(filepath)

        return str(filepath)

    # =========================================
    # 11. EXPORT INVENTORY REPORT TO PDF
    # =========================================

    def export_inventory_pdf(self):

        with self.db.connect() as conn:
            products = conn.execute("""
                SELECT
                    p.sku,
                    p.name,
                    p.category,
                    s.name AS supplier,
                    p.quantity,
                    p.reorder_level,
                    p.unit_cost,
                    p.selling_price,
                    (p.quantity * p.unit_cost) AS inventory_value
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                ORDER BY p.name
            """).fetchall()

        summary = self.inventory_summary()
        low_stock = self.low_stock_analysis()

        filename = (
            "inventory_report_"
            + datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".pdf"
        )
        filepath = EXPORT_DIR / filename

        document = SimpleDocTemplate(
            str(filepath),
            pagesize=landscape(A4),
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm
        )

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="ReportSubtitle",
            parent=styles["Normal"],
            textColor=colors.HexColor("#64748B"),
            spaceAfter=8
        ))

        story = []

        story.append(Paragraph("INVENTORY MANAGEMENT REPORT", styles["Title"]))
        story.append(Paragraph(
            f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
            styles["ReportSubtitle"]
        ))
        story.append(Spacer(1, 8))

        summary_data = [
            ["Inventory Summary", "Value"],
            ["Total Products", str(summary["total_products"])],
            ["Total Units", str(summary["total_units"])],
            ["Inventory Cost Value", f"Rs. {summary['total_cost_value']:,.2f}"],
            ["Potential Sales Value", f"Rs. {summary['potential_sales_value']:,.2f}"],
            ["Low Stock Products", str(summary["low_stock_count"])],
            ["Out of Stock Products", str(summary["out_of_stock_count"])]
        ]

        summary_table = Table(summary_data, colWidths=[75 * mm, 55 * mm])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
            ("PADDING", (0, 0), (-1, -1), 6)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 14))

        story.append(Paragraph("Product Inventory", styles["Heading2"]))

        product_data = [[
            "SKU", "Product", "Category", "Supplier", "Qty",
            "Reorder", "Unit Cost", "Selling Price", "Stock Value"
        ]]

        for product in products:
            product_data.append([
                str(product["sku"]),
                str(product["name"]),
                str(product["category"]),
                str(product["supplier"] or "—"),
                str(product["quantity"]),
                str(product["reorder_level"]),
                f"Rs. {product['unit_cost']:,.2f}",
                f"Rs. {product['selling_price']:,.2f}",
                f"Rs. {product['inventory_value']:,.2f}"
            ])

        product_table = Table(
            product_data,
            repeatRows=1,
            colWidths=[22*mm, 35*mm, 25*mm, 30*mm, 13*mm,
                       16*mm, 25*mm, 27*mm, 27*mm]
        )
        product_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#F1F5F9")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 5)
        ]))
        story.append(product_table)
        story.append(Spacer(1, 14))

        story.append(Paragraph("Low Stock Alerts", styles["Heading2"]))

        low_stock_data = [[
            "SKU", "Product", "Category", "Available", "Reorder Level", "Shortage"
        ]]
        for item in low_stock:
            low_stock_data.append([
                str(item["sku"]),
                str(item["name"]),
                str(item["category"]),
                str(item["quantity"]),
                str(item["reorder_level"]),
                str(item["shortage"])
            ])

        if len(low_stock_data) == 1:
            low_stock_data.append(["—", "No low-stock products", "—", "—", "—", "—"])

        low_stock_table = Table(low_stock_data, repeatRows=1)
        low_stock_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#B45309")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("FONTSIZE", (0, 0), (-1, -1), 8)
        ]))
        story.append(low_stock_table)

        document.build(story)

        return str(filepath)

    # =========================================
    # 12. GENERATE INVENTORY CHART
    # =========================================

    def generate_category_chart(self):

        try:
            import matplotlib.pyplot as plt

        except ImportError:
            raise ImportError(
                "Matplotlib is not installed. "
                "Run: pip install matplotlib"
            )

        data = self.category_analysis()

        if not data:
            raise ValueError("No inventory data available.")

        categories = [
            item["category"] for item in data
        ]

        values = [
            item["inventory_value"] or 0 for item in data
        ]

        plt.figure(figsize=(10, 6))

        plt.bar(categories, values)

        plt.title("Category-wise Inventory Valuation")

        plt.xlabel("Product Categories")

        plt.ylabel("Inventory Value (Rs.)")

        plt.xticks(rotation=30)

        plt.grid(axis="y", linestyle="--", alpha=0.4)

        plt.tight_layout()

        plt.show()

    # =========================================
    # 13. GENERATE STOCK DISTRIBUTION CHART
    # =========================================

    def generate_stock_chart(self):

        try:
            import matplotlib.pyplot as plt

        except ImportError:
            raise ImportError(
                "Matplotlib is not installed. "
                "Run: pip install matplotlib"
            )

        with self.db.connect() as conn:

            data = conn.execute("""
                SELECT

                    name,
                    quantity

                FROM products

                ORDER BY quantity DESC

                LIMIT 10
            """).fetchall()

        if not data:
            raise ValueError("No inventory data available.")

        names = [row["name"] for row in data]

        quantities = [row["quantity"] for row in data]

        plt.figure(figsize=(10, 6))

        plt.barh(names, quantities)

        plt.title("Top 10 Products by Stock Quantity")

        plt.xlabel("Available Quantity")

        plt.ylabel("Product Name")

        plt.tight_layout()

        plt.show()

    # =========================================
    # 14. GENERATE STOCK MOVEMENT CHART
    # =========================================

    def generate_movement_chart(self):

        try:
            import matplotlib.pyplot as plt

        except ImportError:
            raise ImportError(
                "Matplotlib is not installed. "
                "Run: pip install matplotlib"
            )

        data = self.stock_movement_analysis()

        types = [
            row["transaction_type"] for row in data
        ]

        quantities = [
            row["total_quantity"] or 0 for row in data
        ]

        if not data:
            raise ValueError("No transaction data available.")

        plt.figure(figsize=(7, 5))

        plt.bar(types, quantities)

        plt.title("Stock Movement Analysis")

        plt.xlabel("Transaction Type")

        plt.ylabel("Total Quantity")

        plt.tight_layout()

        plt.show()


# =========================================
# BASIC TEST
# =========================================

if __name__ == "__main__":

    reports = ReportManager()

    print("\n===== INVENTORY SUMMARY =====")

    summary = reports.inventory_summary()

    for key, value in summary.items():
        print(key, ":", value)

    print("\n===== CATEGORY ANALYSIS =====")

    for item in reports.category_analysis():
        print(item)

    print("\n===== LOW STOCK PRODUCTS =====")

    for item in reports.low_stock_analysis():
        print(item)

    print("\n===== REORDER RECOMMENDATIONS =====")

    for item in reports.reorder_recommendations():
        print(item)

    print("\n===== PROFIT MARGIN ANALYSIS =====")

    for item in reports.profit_margin_analysis():
        print(item)

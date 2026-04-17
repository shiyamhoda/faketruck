# ============================================================
# AutoParts Data Platform
# Module  : seed_fact_sales.py
# Purpose : Seed fact.FactSales with sample transactional data
# Sprint  : 3
# ============================================================

import os
import sys

if __package__ in (None, ""):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from python.config.db_config import get_db_engine
from python.seed._seed_utils import insert_rows
from python.utils.logger import get_logger

log = get_logger(__name__)

SALES_LINES = [
    ("SO-1001", 1, "2024-01-15", "BP-001", "C001", "STR-001", "SUP-001", 2, 89.99, 0.00, 23.50),
    ("SO-1001", 2, "2024-01-15", "BR-001", "C001", "STR-001", "SUP-001", 2, 119.99, 15.00, 34.20),
    ("SO-1002", 1, "2024-01-16", "OF-001", "C006", "STR-002", "SUP-004", 3, 12.99, 0.00, 4.50),
    ("SO-1003", 1, "2024-01-17", "AF-001", "C007", "STR-003", "SUP-004", 1, 29.99, 2.00, 12.00),
    ("SO-1004", 1, "2024-01-18", "BAT-001", "C003", "WH-001", "SUP-003", 4, 159.99, 25.00, 75.00),
    ("SO-1005", 1, "2024-01-19", "OFL-001", "C008", "ECOM-001", "SUP-007", 2, 34.99, 0.00, 18.00),
    ("SO-1005", 2, "2024-01-19", "OF-002", "C008", "ECOM-001", "SUP-004", 1, 17.99, 0.00, 7.00),
    ("SO-1006", 1, "2024-01-20", "SP-001", "C010", "STR-007", "SUP-002", 8, 18.99, 12.00, 8.50),
    ("SO-1007", 1, "2024-01-21", "BLT-002", "C012", "STR-009", "SUP-005", 1, 139.99, 10.00, 65.00),
    ("SO-1008", 1, "2024-01-22", "WP-001", "C014", "STR-010", "SUP-009", 2, 99.99, 5.00, 45.00),
    ("SO-1009", 1, "2024-01-23", "LMP-003", "C017", "ECOM-001", "SUP-008", 1, 119.99, 0.00, 55.00),
    ("SO-1010", 1, "2024-01-24", "SUS-001", "C018", "STR-005", "SUP-006", 2, 119.99, 8.00, 55.00),
    ("SO-1011", 1, "2024-01-25", "CLT-001", "C020", "STR-006", "SUP-007", 3, 19.99, 0.00, 8.00),
    ("SO-1012", 1, "2024-02-01", "RAD-001", "C004", "WH-001", "SUP-010", 1, 249.99, 20.00, 120.00),
    ("SO-1013", 1, "2024-02-02", "WB-001", "UNKNOWN", "ECOM-001", None, 2, 22.99, 0.00, 9.00),
    ("SO-1013", 2, "2024-02-02", "WW-001", "UNKNOWN", "ECOM-001", None, 1, 9.99, 0.00, 5.00),
    ("SO-1014", 1, "2024-02-03", "TH-001", "C002", "STR-002", "SUP-005", 2, 27.99, 0.00, 12.00),
    ("SO-1015", 1, "2024-02-05", "CF-001", "C013", "STR-007", "SUP-004", 1, 22.99, 1.50, 9.00),
    ("SO-1016", 1, "2024-02-06", "BAT-002", "C011", "STR-008", "SUP-003", 2, 199.99, 15.00, 95.00),
    ("SO-1017", 1, "2024-02-07", "SP-003", "C015", "STR-010", "SUP-003", 6, 14.99, 5.00, 6.00),
]

INSERT_SQL = """
INSERT INTO fact.FactSales (
    OrderNumber, OrderLineNumber, OrderDateKey, ProductKey, CustomerKey, StoreKey,
    SupplierKey, Quantity, UnitPrice, ExtendedAmount, DiscountAmount, NetSalesAmount,
    TaxAmount, TotalAmount, UnitCost, TotalCost, GrossProfitAmount
)
VALUES (
    :OrderNumber, :OrderLineNumber, :OrderDateKey, :ProductKey, :CustomerKey, :StoreKey,
    :SupplierKey, :Quantity, :UnitPrice, :ExtendedAmount, :DiscountAmount, :NetSalesAmount,
    :TaxAmount, :TotalAmount, :UnitCost, :TotalCost, :GrossProfitAmount
)
"""


def _fetch_dimension_map(conn, sql: str) -> dict:
    from sqlalchemy import text

    return {row[0]: row[1] for row in conn.execute(text(sql)).fetchall()}


def build_sales_rows() -> list[dict]:
    engine = get_db_engine("warehouse")
    with engine.connect() as conn:
        product_map = _fetch_dimension_map(
            conn,
            """
            SELECT PartNumber, ProductKey
            FROM dim.DimProduct
            WHERE IsCurrent = 1
            """,
        )
        customer_map = _fetch_dimension_map(
            conn,
            """
            SELECT CustomerCode, CustomerKey
            FROM dim.DimCustomer
            WHERE IsCurrent = 1
            """,
        )
        store_map = _fetch_dimension_map(
            conn,
            "SELECT StoreCode, StoreKey FROM dim.DimStore WHERE IsActive = 1",
        )
        supplier_map = _fetch_dimension_map(
            conn,
            "SELECT SupplierCode, SupplierKey FROM dim.DimSupplier WHERE IsActive = 1",
        )

    rows = []
    for order_number, line_number, order_date, part_number, customer_code, store_code, supplier_code, quantity, unit_price, discount_amount, unit_cost in SALES_LINES:
        order_date_key = int(order_date.replace("-", ""))
        extended_amount = round(quantity * unit_price, 2)
        net_sales_amount = round(extended_amount - discount_amount, 2)
        tax_amount = round(net_sales_amount * 0.13, 2)
        total_amount = round(net_sales_amount + tax_amount, 2)
        total_cost = round(quantity * unit_cost, 2)
        gross_profit_amount = round(net_sales_amount - total_cost, 2)

        if part_number not in product_map:
            raise ValueError(f"Missing product in DimProduct: {part_number}")
        if customer_code not in customer_map:
            raise ValueError(f"Missing customer in DimCustomer: {customer_code}")
        if store_code not in store_map:
            raise ValueError(f"Missing store in DimStore: {store_code}")
        if supplier_code and supplier_code not in supplier_map:
            raise ValueError(f"Missing supplier in DimSupplier: {supplier_code}")

        rows.append({
            "OrderNumber": order_number,
            "OrderLineNumber": line_number,
            "OrderDateKey": order_date_key,
            "ProductKey": product_map[part_number],
            "CustomerKey": customer_map[customer_code],
            "StoreKey": store_map[store_code],
            "SupplierKey": supplier_map.get(supplier_code),
            "Quantity": quantity,
            "UnitPrice": unit_price,
            "ExtendedAmount": extended_amount,
            "DiscountAmount": discount_amount,
            "NetSalesAmount": net_sales_amount,
            "TaxAmount": tax_amount,
            "TotalAmount": total_amount,
            "UnitCost": unit_cost,
            "TotalCost": total_cost,
            "GrossProfitAmount": gross_profit_amount,
        })

    return rows


def seed(truncate: bool = False) -> int:
    from sqlalchemy import text

    engine = get_db_engine("warehouse")
    with engine.begin() as conn:
        if truncate:
            conn.execute(text("TRUNCATE TABLE fact.FactSales"))
            log.info("fact.FactSales truncated.")
        existing = conn.execute(text("SELECT COUNT(*) FROM fact.FactSales")).scalar()

    if existing and not truncate:
        log.info(f"fact.FactSales already has {existing} rows - skipping.")
        return existing

    rows = build_sales_rows()
    insert_rows(engine, INSERT_SQL, rows, chunksize=200)
    log.info(f"fact.FactSales seeded: {len(rows)} rows.")
    return len(rows)


if __name__ == "__main__":
    seed()

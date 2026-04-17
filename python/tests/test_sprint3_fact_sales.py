# ============================================================
# AutoParts Data Platform
# Module  : test_sprint3_fact_sales.py
# Purpose : Live tests for fact.FactSales and dimensional integrity
# Run     : pytest python/tests/test_sprint3_fact_sales.py -v --live
# Sprint  : 3
# ============================================================

import os
import sys

import pytest
from sqlalchemy import text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from python.config.db_config import get_db_engine

pytestmark = pytest.mark.live


def query_scalar(engine, sql: str):
    with engine.connect() as conn:
        return conn.execute(text(sql)).scalar()


def query_set(engine, sql: str) -> set:
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
    return {row[0] for row in rows}


class TestFactSales:

    def test_factsales_table_exists(self):
        engine = get_db_engine("warehouse")
        count = query_scalar(
            engine,
            """
            SELECT COUNT(*)
            FROM sys.tables t
            JOIN sys.schemas s ON t.schema_id = s.schema_id
            WHERE s.name = 'fact' AND t.name = 'FactSales'
            """,
        )
        assert count == 1, "fact.FactSales not found in AutoParts_DW"

    def test_factsales_columns_exist(self):
        required_columns = {
            "SalesKey", "OrderNumber", "OrderLineNumber", "OrderDateKey",
            "ProductKey", "CustomerKey", "StoreKey", "SupplierKey",
            "Quantity", "UnitPrice", "ExtendedAmount", "DiscountAmount",
            "NetSalesAmount", "TaxAmount", "TotalAmount", "UnitCost",
            "TotalCost", "GrossProfitAmount", "CreatedAt",
        }
        engine = get_db_engine("warehouse")
        columns = query_set(
            engine,
            """
            SELECT c.name
            FROM sys.columns c
            JOIN sys.tables t ON c.object_id = t.object_id
            JOIN sys.schemas s ON t.schema_id = s.schema_id
            WHERE s.name = 'fact' AND t.name = 'FactSales'
            """,
        )
        missing = required_columns - columns
        assert not missing, f"FactSales missing columns: {missing}"

    def test_factsales_has_rows(self):
        engine = get_db_engine("warehouse")
        count = query_scalar(engine, "SELECT COUNT(*) FROM fact.FactSales")
        assert count >= 20, f"Expected at least 20 rows in fact.FactSales, got {count}"

    def test_factsales_foreign_keys_are_resolved(self):
        engine = get_db_engine("warehouse")
        count = query_scalar(
            engine,
            """
            SELECT COUNT(*)
            FROM fact.FactSales fs
            LEFT JOIN dim.DimDate dd      ON fs.OrderDateKey = dd.DateKey
            LEFT JOIN dim.DimProduct dp   ON fs.ProductKey = dp.ProductKey
            LEFT JOIN dim.DimCustomer dc  ON fs.CustomerKey = dc.CustomerKey
            LEFT JOIN dim.DimStore ds     ON fs.StoreKey = ds.StoreKey
            LEFT JOIN dim.DimSupplier dsp ON fs.SupplierKey = dsp.SupplierKey
            WHERE dd.DateKey IS NULL
               OR dp.ProductKey IS NULL
               OR dc.CustomerKey IS NULL
               OR ds.StoreKey IS NULL
               OR (fs.SupplierKey IS NOT NULL AND dsp.SupplierKey IS NULL)
            """,
        )
        assert count == 0, "FactSales contains unresolved foreign keys"

    def test_factsales_financials_are_consistent(self):
        engine = get_db_engine("warehouse")
        count = query_scalar(
            engine,
            """
            SELECT COUNT(*)
            FROM fact.FactSales
            WHERE ExtendedAmount <> ROUND(Quantity * UnitPrice, 2)
               OR NetSalesAmount <> ROUND(ExtendedAmount - DiscountAmount, 2)
               OR TotalAmount <> ROUND(NetSalesAmount + TaxAmount, 2)
               OR TotalCost <> ROUND(Quantity * UnitCost, 2)
               OR GrossProfitAmount <> ROUND(NetSalesAmount - TotalCost, 2)
            """,
        )
        assert count == 0, "FactSales contains inconsistent financial calculations"

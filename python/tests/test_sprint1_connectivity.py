# ============================================================
# AutoParts Data Platform
# Module  : test_sprint1_connectivity.py
# Purpose : Live DB connectivity tests — requires SQL Server
# Run     : pytest python/tests/test_sprint1_connectivity.py -v
#           Skip with: pytest -m "not live"
# Sprint  : 1
# ============================================================

import sys
import os
import pytest
from sqlalchemy import text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from python.config.db_config import get_db_engine

# Mark all tests as live
pytestmark = pytest.mark.live


def get_conn(layer: str):
    """Helper: open a SQLAlchemy connection."""
    engine = get_db_engine(layer)
    return engine.connect()


class TestStagingConnectivity:

    def test_can_connect_to_staging(self):
        with get_conn("staging") as conn:
            assert conn is not None

    def test_staging_schemas_exist(self):
        expected = {"pos", "ecom", "inventory", "supplier"}

        with get_conn("staging") as conn:
            result = conn.execute(text("SELECT name FROM sys.schemas"))
            schemas = {row[0] for row in result.fetchall()}

        assert expected.issubset(schemas), (
            f"Missing schemas: {expected - schemas}"
        )


class TestODSConnectivity:

    def test_can_connect_to_ods(self):
        with get_conn("ods") as conn:
            assert conn is not None

    def test_ods_schema_exists(self):
        with get_conn("ods") as conn:
            result = conn.execute(
                text("SELECT COUNT(*) FROM sys.schemas WHERE name = 'ods'")
            )
            count = result.scalar()

        assert count == 1, "[ods] schema not found in AutoParts_ODS"


class TestWarehouseConnectivity:

    def test_can_connect_to_warehouse(self):
        with get_conn("warehouse") as conn:
            assert conn is not None

    def test_dw_schemas_exist(self):
        expected = {"dim", "fact", "meta"}

        with get_conn("warehouse") as conn:
            result = conn.execute(text("SELECT name FROM sys.schemas"))
            schemas = {row[0] for row in result.fetchall()}

        assert expected.issubset(schemas), (
            f"Missing DW schemas: {expected - schemas}"
        )

    def test_loadlog_table_exists(self):
        with get_conn("warehouse") as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) FROM sys.tables t
                JOIN sys.schemas s ON t.schema_id = s.schema_id
                WHERE s.name = 'meta' AND t.name = 'LoadLog'
            """))
            count = result.scalar()

        assert count == 1, "meta.LoadLog not found"

    def test_loadlog_insert_and_cleanup(self):
        with get_conn("warehouse") as conn:

            # Insert
            conn.execute(text("""
                INSERT INTO meta.LoadLog (TableName, Status)
                VALUES ('PYTEST_SMOKE', 'Running')
            """))
            conn.commit()

            # Validate insert
            result = conn.execute(text("""
                SELECT COUNT(*) FROM meta.LoadLog
                WHERE TableName = 'PYTEST_SMOKE'
            """))
            count = result.scalar()
            assert count >= 1, "Inserted row not found"

            # Cleanup
            conn.execute(text("""
                DELETE FROM meta.LoadLog
                WHERE TableName = 'PYTEST_SMOKE'
            """))
            conn.commit()
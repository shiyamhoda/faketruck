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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from python.config.db_config import get_connection_string

# Mark all tests in this file as "live" so they can be skipped in CI
pytestmark = pytest.mark.live

try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False

skip_no_pyodbc = pytest.mark.skipif(
    not PYODBC_AVAILABLE,
    reason="pyodbc not installed"
)


def get_conn(layer: str):
    """Helper: open a pyodbc connection for a given layer."""
    return pyodbc.connect(get_connection_string(layer), timeout=5)


@skip_no_pyodbc
class TestStagingConnectivity:

    def test_can_connect_to_staging(self):
        """Must be able to open a connection to AutoParts_Staging."""
        with get_conn("staging") as conn:
            assert conn is not None

    def test_staging_schemas_exist(self):
        """All four staging schemas must be present."""
        expected = {"pos", "ecom", "inventory", "supplier"}
        with get_conn("staging") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sys.schemas")
            schemas = {row.name for row in cursor.fetchall()}
        assert expected.issubset(schemas), (
            f"Missing schemas: {expected - schemas}"
        )


@skip_no_pyodbc
class TestODSConnectivity:

    def test_can_connect_to_ods(self):
        """Must be able to open a connection to AutoParts_ODS."""
        with get_conn("ods") as conn:
            assert conn is not None

    def test_ods_schema_exists(self):
        """[ods] schema must exist in AutoParts_ODS."""
        with get_conn("ods") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM sys.schemas WHERE name = 'ods'"
            )
            count = cursor.fetchone()[0]
        assert count == 1, "[ods] schema not found in AutoParts_ODS"


@skip_no_pyodbc
class TestWarehouseConnectivity:

    def test_can_connect_to_warehouse(self):
        """Must be able to open a connection to AutoParts_DW."""
        with get_conn("warehouse") as conn:
            assert conn is not None

    def test_dw_schemas_exist(self):
        """dim, fact, and meta schemas must exist in AutoParts_DW."""
        expected = {"dim", "fact", "meta"}
        with get_conn("warehouse") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sys.schemas")
            schemas = {row.name for row in cursor.fetchall()}
        assert expected.issubset(schemas), (
            f"Missing DW schemas: {expected - schemas}"
        )

    def test_loadlog_table_exists(self):
        """meta.LoadLog must exist in AutoParts_DW."""
        with get_conn("warehouse") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM sys.tables t
                JOIN sys.schemas s ON t.schema_id = s.schema_id
                WHERE s.name = 'meta' AND t.name = 'LoadLog'
            """)
            count = cursor.fetchone()[0]
        assert count == 1, "meta.LoadLog not found"

    def test_loadlog_insert_and_cleanup(self):
        """Must be able to insert a test row into LoadLog and delete it."""
        with get_conn("warehouse") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO meta.LoadLog (TableName, Status)
                VALUES ('PYTEST_SMOKE', 'Running')
            """)
            conn.commit()

            cursor.execute("""
                SELECT COUNT(*) FROM meta.LoadLog
                WHERE TableName = 'PYTEST_SMOKE'
            """)
            count = cursor.fetchone()[0]
            assert count >= 1, "Inserted row not found"

            cursor.execute("""
                DELETE FROM meta.LoadLog WHERE TableName = 'PYTEST_SMOKE'
            """)
            conn.commit()
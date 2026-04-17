# ============================================================
# AutoParts Data Platform
# Module  : test_sprint1_connectivity.py
# Purpose : Live DB connectivity tests via SQLAlchemy engine
# Run     : pytest python/tests/test_sprint1_connectivity.py -v --live
# Sprint  : 1 — Refactored for SQLAlchemy engine
# ============================================================

import sys
import os
import pytest
from sqlalchemy import text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from python.config.db_config import get_db_engine

pytestmark = pytest.mark.live


def query_scalar(engine, sql: str) -> any:
    """Execute a scalar query and return the single value."""
    with engine.connect() as conn:
        return conn.execute(text(sql)).scalar()


def query_set(engine, sql: str) -> set:
    """Execute a query and return results as a set of first-column values."""
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
    return {row[0] for row in rows}


class TestStagingConnectivity:

    def test_can_connect_to_staging(self):
        """Must open a live connection to AutoParts_Staging."""
        engine = get_db_engine("staging")
        with engine.connect() as conn:
            assert conn is not None

    def test_staging_is_correct_database(self):
        """Connected database must be AutoParts_Staging."""
        engine  = get_db_engine("staging")
        db_name = query_scalar(engine, "SELECT DB_NAME()")
        assert db_name == "AutoParts_Staging", (
            f"Expected 'AutoParts_Staging', got '{db_name}'"
        )

    def test_staging_schemas_exist(self):
        """All four staging schemas must exist."""
        expected = {"pos", "ecom", "inventory", "supplier"}
        engine   = get_db_engine("staging")
        schemas  = query_set(engine, "SELECT name FROM sys.schemas")
        missing  = expected - schemas
        assert not missing, f"Missing staging schemas: {missing}"

    def test_staging_can_execute_simple_query(self):
        """Must be able to run a basic SELECT on staging."""
        engine = get_db_engine("staging")
        result = query_scalar(engine, "SELECT 1")
        assert result == 1


class TestODSConnectivity:

    def test_can_connect_to_ods(self):
        """Must open a live connection to AutoParts_ODS."""
        engine = get_db_engine("ods")
        with engine.connect() as conn:
            assert conn is not None

    def test_ods_is_correct_database(self):
        """Connected database must be AutoParts_ODS."""
        engine  = get_db_engine("ods")
        db_name = query_scalar(engine, "SELECT DB_NAME()")
        assert db_name == "AutoParts_ODS", (
            f"Expected 'AutoParts_ODS', got '{db_name}'"
        )

    def test_ods_schema_exists(self):
        """[ods] schema must exist in AutoParts_ODS."""
        engine = get_db_engine("ods")
        count  = query_scalar(
            engine,
            "SELECT COUNT(*) FROM sys.schemas WHERE name = 'ods'"
        )
        assert count == 1, "[ods] schema not found in AutoParts_ODS"

    def test_ods_can_execute_simple_query(self):
        """Must be able to run a basic SELECT on ODS."""
        engine = get_db_engine("ods")
        result = query_scalar(engine, "SELECT 1")
        assert result == 1


class TestWarehouseConnectivity:

    def test_can_connect_to_warehouse(self):
        """Must open a live connection to AutoParts_DW."""
        engine = get_db_engine("warehouse")
        with engine.connect() as conn:
            assert conn is not None

    def test_warehouse_is_correct_database(self):
        """Connected database must be AutoParts_DW."""
        engine  = get_db_engine("warehouse")
        db_name = query_scalar(engine, "SELECT DB_NAME()")
        assert db_name == "AutoParts_DW", (
            f"Expected 'AutoParts_DW', got '{db_name}'"
        )

    def test_dw_schemas_exist(self):
        """dim, fact, and meta schemas must all exist in AutoParts_DW."""
        expected = {"dim", "fact", "meta"}
        engine   = get_db_engine("warehouse")
        schemas  = query_set(engine, "SELECT name FROM sys.schemas")
        missing  = expected - schemas
        assert not missing, f"Missing DW schemas: {missing}"

    def test_loadlog_table_exists(self):
        """meta.LoadLog table must exist in AutoParts_DW."""
        engine = get_db_engine("warehouse")
        count  = query_scalar(engine, """
            SELECT COUNT(*) FROM sys.tables t
            JOIN sys.schemas s ON t.schema_id = s.schema_id
            WHERE s.name = 'meta' AND t.name = 'LoadLog'
        """)
        assert count == 1, "meta.LoadLog not found in AutoParts_DW"

    def test_loadlog_columns_exist(self):
        """All required LoadLog columns must be present."""
        required_columns = {
            "LoadLogID", "BatchID", "TableName",
            "LoadStart", "LoadEnd", "RowsInserted",
            "RowsUpdated", "Status", "ErrorMessage"
        }
        engine  = get_db_engine("warehouse")
        columns = query_set(engine, """
            SELECT c.name FROM sys.columns c
            JOIN sys.tables t  ON c.object_id = t.object_id
            JOIN sys.schemas s ON t.schema_id  = s.schema_id
            WHERE s.name = 'meta' AND t.name = 'LoadLog'
        """)
        missing = required_columns - columns
        assert not missing, f"LoadLog missing columns: {missing}"

    def test_loadlog_insert_and_cleanup(self):
        """Must insert a test row into LoadLog, confirm it, then delete it."""
        engine = get_db_engine("warehouse")
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO meta.LoadLog (TableName, Status)
                VALUES ('PYTEST_SMOKE', 'Running')
            """))

        count = query_scalar(engine, """
            SELECT COUNT(*) FROM meta.LoadLog
            WHERE TableName = 'PYTEST_SMOKE'
        """)
        assert count >= 1, "Inserted PYTEST_SMOKE row not found"

        with engine.begin() as conn:
            conn.execute(text("""
                DELETE FROM meta.LoadLog WHERE TableName = 'PYTEST_SMOKE'
            """))

    def test_loadlog_status_default_is_running(self):
        """LoadLog Status column default must be 'Running'."""
        engine = get_db_engine("warehouse")
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO meta.LoadLog (TableName)
                VALUES ('PYTEST_DEFAULT_CHECK')
            """))
        status = query_scalar(engine, """
            SELECT TOP 1 Status FROM meta.LoadLog
            WHERE TableName = 'PYTEST_DEFAULT_CHECK'
        """)
        with engine.begin() as conn:
            conn.execute(text("""
                DELETE FROM meta.LoadLog WHERE TableName = 'PYTEST_DEFAULT_CHECK'
            """))
        assert status == "Running", (
            f"Expected default Status='Running', got '{status}'"
        )

    def test_warehouse_can_execute_simple_query(self):
        """Must be able to run a basic SELECT on the warehouse."""
        engine = get_db_engine("warehouse")
        result = query_scalar(engine, "SELECT 1")
        assert result == 1
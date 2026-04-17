# ============================================================
# AutoParts Data Platform
# Module  : test_sprint1_config.py
# Purpose : Pytest unit tests for db_config and logger
# Run     : pytest python/tests/ -v
# Sprint  : 1 — Refactored for SQLAlchemy engine
# ============================================================

import sys
import os
import logging
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from python.config.db_config import DB_CONFIG, get_db_engine
from python.utils.logger import get_logger


class TestDbConfig:

    def test_all_layers_present(self):
        """Config must define staging, ods, and warehouse layers."""
        for layer in ("staging", "ods", "warehouse"):
            assert layer in DB_CONFIG, f"Missing layer: {layer}"

    def test_each_layer_has_required_keys(self):
        """Every layer config must have server, database, driver, and trusted."""
        required = {"server", "database", "driver", "trusted"}
        for layer, cfg in DB_CONFIG.items():
            missing = required - cfg.keys()
            assert not missing, f"Layer '{layer}' missing keys: {missing}"

    def test_database_names_are_correct(self):
        """Database names must match expected values."""
        assert DB_CONFIG["staging"]["database"]  == "AutoParts_Staging"
        assert DB_CONFIG["ods"]["database"]       == "AutoParts_ODS"
        assert DB_CONFIG["warehouse"]["database"] == "AutoParts_DW"

    def test_server_is_consistent_across_layers(self):
        """All layers must point to the same server."""
        servers = {cfg["server"] for cfg in DB_CONFIG.values()}
        assert len(servers) == 1, (
            f"Layers point to different servers: {servers}"
        )

    def test_server_name_is_not_empty(self):
        """Server name must not be empty in any layer."""
        for layer, cfg in DB_CONFIG.items():
            assert cfg["server"].strip(), f"Layer '{layer}' has empty server"

    def test_trusted_is_boolean(self):
        """Trusted flag must be a boolean in all layers."""
        for layer, cfg in DB_CONFIG.items():
            assert isinstance(cfg["trusted"], bool), (
                f"Layer '{layer}' trusted flag is not bool: {type(cfg['trusted'])}"
            )

    def test_get_db_engine_returns_engine_for_all_layers(self):
        """get_db_engine must return a SQLAlchemy engine for each layer."""
        from sqlalchemy.engine import Engine
        for layer in ("staging", "ods", "warehouse"):
            engine = get_db_engine(layer)
            assert isinstance(engine, Engine), (
                f"Layer '{layer}' did not return a SQLAlchemy Engine"
            )

    def test_get_db_engine_invalid_layer_raises_value_error(self):
        """Requesting an unknown layer must raise ValueError."""
        with pytest.raises(ValueError, match="Invalid layer"):
            get_db_engine("nonexistent")

    def test_engine_url_contains_correct_database(self):
        """Each engine URL must reference the correct database."""
        expected = {
            "staging":   "AutoParts_Staging",
            "ods":       "AutoParts_ODS",
            "warehouse": "AutoParts_DW",
        }
        for layer, db_name in expected.items():
            engine = get_db_engine(layer)
            assert engine.url.database == db_name, (
                f"Layer '{layer}': expected DB '{db_name}', "
                f"got '{engine.url.database}'"
            )

    def test_engine_url_contains_correct_server(self):
        """Each engine URL must reference the configured server."""
        for layer, cfg in DB_CONFIG.items():
            engine = get_db_engine(layer)
            assert cfg["server"] in str(engine.url), (
                f"Layer '{layer}': server '{cfg['server']}' "
                f"not found in engine URL"
            )

    def test_engine_uses_mssql_pyodbc_dialect(self):
        """Engine must use the mssql+pyodbc dialect."""
        for layer in ("staging", "ods", "warehouse"):
            engine = get_db_engine(layer)
            assert engine.dialect.name == "mssql", (
                f"Layer '{layer}': expected dialect 'mssql', "
                f"got '{engine.dialect.name}'"
            )

    def test_env_override_database_name(self, monkeypatch):
        """DB_STAGING env var must override the staging database name."""
        monkeypatch.setenv("DB_STAGING", "AutoParts_Staging_Test")
        import importlib
        import python.config.db_config as cfg_module
        importlib.reload(cfg_module)
        assert cfg_module.DB_CONFIG["staging"]["database"] == "AutoParts_Staging_Test"
        # Restore
        monkeypatch.delenv("DB_STAGING")
        importlib.reload(cfg_module)

    def test_multiple_engines_are_independent(self):
        """Engines for different layers must not share the same URL."""
        engine_staging   = get_db_engine("staging")
        engine_warehouse = get_db_engine("warehouse")
        assert engine_staging.url.database != engine_warehouse.url.database


class TestLogger:

    def test_get_logger_returns_logger(self):
        """get_logger must return a logging.Logger instance."""
        logger = get_logger("test.module")
        assert isinstance(logger, logging.Logger)

    def test_logger_has_handlers(self):
        """Logger must have at least one handler attached."""
        logger = get_logger("test.handlers")
        assert len(logger.handlers) >= 1

    def test_logger_level_is_debug(self):
        """Logger root level must be DEBUG."""
        logger = get_logger("test.level")
        assert logger.level == logging.DEBUG

    def test_same_name_returns_same_instance(self):
        """Calling get_logger twice with the same name returns the same object."""
        a = get_logger("test.singleton")
        b = get_logger("test.singleton")
        assert a is b

    def test_logger_can_write_without_error(self):
        """Logger must write a message without raising an exception."""
        logger = get_logger("test.write")
        try:
            logger.info("Sprint 1 smoke test log entry")
        except Exception as e:
            assert False, f"Logger raised an exception: {e}"

    def test_file_handler_present(self):
        """Logger must include a FileHandler for persistent logs."""
        logger = get_logger("test.filehandler")
        has_file_handler = any(
            isinstance(h, logging.FileHandler) for h in logger.handlers
        )
        assert has_file_handler, "No FileHandler found on logger"

    def test_stream_handler_present(self):
        """Logger must include a StreamHandler for console output."""
        logger = get_logger("test.streamhandler")
        has_stream_handler = any(
            isinstance(h, logging.StreamHandler) for h in logger.handlers
        )
        assert has_stream_handler, "No StreamHandler found on logger"
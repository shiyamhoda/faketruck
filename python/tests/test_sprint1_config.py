# ============================================================
# AutoParts Data Platform
# Module  : test_sprint1_config.py
# Purpose : Pytest unit tests for db_config and logger
# Run     : pytest python/tests/ -v
# Sprint  : 1
# ============================================================

import sys
import os
import logging

# Make sure project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from python.config.db_config import DB_CONFIG, get_connection_string
from python.utils.logger import get_logger


class TestDbConfig:

    def test_all_layers_present(self):
        """Config must define staging, ods, and warehouse layers."""
        for layer in ("staging", "ods", "warehouse"):
            assert layer in DB_CONFIG, f"Missing layer: {layer}"

    def test_each_layer_has_required_keys(self):
        """Every layer config must have server, database, and driver."""
        required = {"server", "database", "driver"}
        for layer, cfg in DB_CONFIG.items():
            missing = required - cfg.keys()
            assert not missing, f"Layer '{layer}' missing keys: {missing}"

    def test_database_names_are_correct(self):
        """Database names must match expected values."""
        assert DB_CONFIG["staging"]["database"]   == "AutoParts_Staging"
        assert DB_CONFIG["ods"]["database"]        == "AutoParts_ODS"
        assert DB_CONFIG["warehouse"]["database"]  == "AutoParts_DW"

    def test_connection_string_trusted_contains_required_parts(self):
        """Trusted connection string must include SERVER, DATABASE, Trusted_Connection."""
        for layer in ("staging", "ods", "warehouse"):
            conn = get_connection_string(layer)
            assert "SERVER="            in conn, f"{layer}: missing SERVER"
            assert "DATABASE="          in conn, f"{layer}: missing DATABASE"
            assert "Trusted_Connection" in conn, f"{layer}: missing Trusted_Connection"

    def test_connection_string_contains_correct_db_name(self):
        """Each layer's connection string must reference its own database."""
        expected = {
            "staging":   "AutoParts_Staging",
            "ods":       "AutoParts_ODS",
            "warehouse": "AutoParts_DW",
        }
        for layer, db_name in expected.items():
            conn = get_connection_string(layer)
            assert db_name in conn, f"{layer}: expected '{db_name}' in connection string"

    def test_env_override_server(self, monkeypatch):
        """DB_SERVER env var must override the server value."""
        monkeypatch.setenv("DB_SERVER", "my-test-server")
        # Re-import to pick up env change
        import importlib
        import python.config.db_config as cfg_module
        importlib.reload(cfg_module)
        conn = cfg_module.get_connection_string("staging")
        assert "my-test-server" in conn

    def test_invalid_layer_raises_key_error(self):
        """Requesting an unknown layer must raise KeyError."""
        try:
            get_connection_string("nonexistent")
            assert False, "Expected KeyError not raised"
        except KeyError:
            pass


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

    def test_logger_can_write_without_error(self, tmp_path, monkeypatch):
        """Logger must write a message without raising an exception."""
        monkeypatch.setenv("LOG_DIR", str(tmp_path))
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
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
import importlib

# Make sure project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from python.config.db_config import DB_CONFIG, get_db_engine
from python.utils.logger import get_logger


class TestDbConfig:

    def test_all_layers_present(self):
        for layer in ("staging", "ods", "warehouse"):
            assert layer in DB_CONFIG, f"Missing layer: {layer}"

    def test_each_layer_has_required_keys(self):
        required = {"server", "database", "driver"}
        for layer, cfg in DB_CONFIG.items():
            missing = required - cfg.keys()
            assert not missing, f"Layer '{layer}' missing keys: {missing}"

    def test_database_names_are_correct(self):
        assert DB_CONFIG["staging"]["database"]   == "AutoParts_Staging"
        assert DB_CONFIG["ods"]["database"]       == "AutoParts_ODS"
        assert DB_CONFIG["warehouse"]["database"] == "AutoParts_DW"

    def test_engine_creation(self):
        """Engine should be created successfully for all layers."""
        for layer in ("staging", "ods", "warehouse"):
            engine = get_db_engine(layer)
            assert engine is not None

    def test_engine_url_contains_expected_parts(self):
        """Engine URL must contain driver and database name."""
        expected = {
            "staging":   "AutoParts_Staging",
            "ods":       "AutoParts_ODS",
            "warehouse": "AutoParts_DW",
        }

        for layer, db_name in expected.items():
            engine = get_db_engine(layer)
            url = str(engine.url)

            assert "mssql+pyodbc" in url, f"{layer}: missing driver"
            assert db_name in url, f"{layer}: expected '{db_name}' in URL"

    def test_env_override_server(self, monkeypatch):
        """DB_SERVER env var must override the server value."""
        monkeypatch.setenv("DB_SERVER", "my-test-server")

        import python.config.db_config as cfg_module
        importlib.reload(cfg_module)

        engine = cfg_module.get_db_engine("staging")
        url = str(engine.url)

        assert "my-test-server" in url

    def test_invalid_layer_raises_value_error(self):
        """Requesting an unknown layer must raise ValueError."""
        try:
            get_db_engine("nonexistent")
            assert False, "Expected ValueError not raised"
        except ValueError:
            pass


class TestLogger:

    def test_get_logger_returns_logger(self):
        logger = get_logger("test.module")
        assert isinstance(logger, logging.Logger)

    def test_logger_has_handlers(self):
        logger = get_logger("test.handlers")
        assert len(logger.handlers) >= 1

    def test_logger_level_is_debug(self):
        logger = get_logger("test.level")
        assert logger.level == logging.DEBUG

    def test_same_name_returns_same_instance(self):
        a = get_logger("test.singleton")
        b = get_logger("test.singleton")
        assert a is b

    def test_logger_can_write_without_error(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LOG_DIR", str(tmp_path))
        logger = get_logger("test.write")

        try:
            logger.info("Sprint 1 smoke test log entry")
        except Exception as e:
            assert False, f"Logger raised an exception: {e}"

    def test_file_handler_present(self):
        logger = get_logger("test.filehandler")

        has_file_handler = any(
            isinstance(h, logging.FileHandler) for h in logger.handlers
        )
        assert has_file_handler, "No FileHandler found on logger"
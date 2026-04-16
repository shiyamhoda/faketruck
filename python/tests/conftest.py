# ============================================================
# AutoParts Data Platform
# Module  : conftest.py
# Purpose : Pytest configuration and shared fixtures
# Sprint  : 1
# ============================================================

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "live: marks tests that require a live SQL Server connection"
    )


def pytest_collection_modifyitems(config, items):
    """Auto-skip 'live' tests unless --live flag is passed."""
    if config.getoption("--live", default=False):
        return
    skip_live = pytest.mark.skip(reason="Live DB tests skipped. Use --live to run.")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


def pytest_addoption(parser):
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Run tests that require a live SQL Server connection"
    )
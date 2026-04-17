# ============================================================
# AutoParts Data Platform
# Script  : diagnose_connection.py
# Purpose : Standalone connection diagnostic via SQLAlchemy
# Usage   : python python/tests/diagnose_connection.py
# Sprint  : 1 — Refactored for SQLAlchemy engine
# ============================================================

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


def check_dependencies():
    missing = []
    for pkg in ("sqlalchemy", "pyodbc"):
        try:
            __import__(pkg)
            print(f"[OK]  {pkg} imported successfully")
        except ImportError:
            print(f"[FAIL] {pkg} not installed — run: pip install {pkg}")
            missing.append(pkg)
    if missing:
        sys.exit(1)


def check_drivers():
    import pyodbc
    drivers = [d for d in pyodbc.drivers() if "SQL Server" in d]
    if drivers:
        for d in drivers:
            print(f"[OK]  ODBC driver found: {d}")
    else:
        print("[FAIL] No SQL Server ODBC drivers found")
        print("       Download: https://aka.ms/downloadmsodbcsql")
        sys.exit(1)


def test_engine(layer: str, description: str):
    from python.config.db_config import get_db_engine
    from sqlalchemy import text

    print(f"\n  Testing layer : {layer} ({description})")
    try:
        engine = get_db_engine(layer)
        print(f"  Engine URL    : {engine.url}")
        with engine.connect() as conn:
            server  = conn.execute(text("SELECT @@SERVERNAME")).scalar()
            db_name = conn.execute(text("SELECT DB_NAME()")).scalar()
            version = conn.execute(text("SELECT @@VERSION")).scalar()
        print(f"[OK]  Connected!  Server={server}  DB={db_name}")
        print(f"      Version: {version[:80]}...")
        return True
    except Exception as e:
        print(f"[FAIL] {str(e)[:150]}")
        return False


def main():
    print("=" * 60)
    print(" AutoParts — SQLAlchemy Connection Diagnostic")
    print("=" * 60)

    check_dependencies()
    check_drivers()

    print(f"\n{'─' * 60}")
    print(" Testing all three database layers...")
    print(f"{'─' * 60}")

    results = {
        "staging":   test_engine("staging",   "AutoParts_Staging"),
        "ods":       test_engine("ods",        "AutoParts_ODS"),
        "warehouse": test_engine("warehouse",  "AutoParts_DW"),
    }

    print(f"\n{'=' * 60}")
    print(" Summary")
    print(f"{'─' * 60}")
    all_passed = True
    for layer, passed in results.items():
        status = "[OK] " if passed else "[FAIL]"
        print(f"  {status}  {layer}")
        if not passed:
            all_passed = False

    if all_passed:
        print()
        print("  All layers connected successfully.")
        print("  You are clear to run the full test suite:")
        print()
        print("    pytest python/tests/test_sprint1_config.py -v")
        print("    pytest python/tests/test_sprint1_connectivity.py -v --live")
    else:
        print()
        print("  One or more layers failed. Check:")
        print("  1. SQL Server Browser service is Running")
        print("  2. TCP/IP enabled in SQL Server Configuration Manager")
        print("  3. Server name in db_config.py matches your instance")
        print(f"     Current: {__import__('python.config.db_config', fromlist=['DB_CONFIG']).DB_CONFIG['staging']['server']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
# ============================================================
# AutoParts Data Platform
# Module  : run_all_seeds.py
# Purpose : Orchestrate warehouse seed scripts in dependency order
# Usage   : python -m python.seed.run_all_seeds
#           python -m python.seed.run_all_seeds --truncate
# Sprint  : 3
# ============================================================

import os
import sys
import time

if __package__ in (None, ""):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from python.utils.logger import get_logger

log = get_logger("seed.orchestrator")


def get_seeds():
    from python.seed import (
        seed_dim_customer,
        seed_dim_date,
        seed_dim_product,
        seed_fact_sales,
        seed_dim_store,
        seed_dim_supplier,
    )

    return [
        ("DimDate", seed_dim_date),
        ("DimProduct", seed_dim_product),
        ("DimCustomer", seed_dim_customer),
        ("DimStore", seed_dim_store),
        ("DimSupplier", seed_dim_supplier),
        ("FactSales", seed_fact_sales),
    ]


def main() -> int:
    truncate = "--truncate" in sys.argv
    if truncate:
        log.warning("--truncate flag set: existing seed data will be cleared.")

    log.info("=" * 50)
    log.info(" AutoParts Sprint 3 - Warehouse Seed Run")
    log.info("=" * 50)

    try:
        seeds = get_seeds()
    except ModuleNotFoundError as exc:
        missing_package = exc.name or "dependency"
        log.error(f"Missing Python package: {missing_package}")
        log.error("Install project dependencies, then re-run the seed script.")
        log.error("Suggested command: pip install -r requirements.txt")
        return 1

    results = {}
    for table, module in seeds:
        log.info(f"Seeding {table}...")
        started_at = time.time()
        try:
            rows = module.seed(truncate=truncate)
            elapsed = round(time.time() - started_at, 2)
            results[table] = ("OK", rows, elapsed)
            log.info(f"  {table}: {rows} rows in {elapsed}s")
        except ModuleNotFoundError as exc:
            results[table] = ("FAIL", 0, 0)
            missing_package = exc.name or "dependency"
            log.error(f"  {table} FAILED: missing Python package '{missing_package}'")
            log.error("  Install project dependencies with: pip install -r requirements.txt")
        except Exception as exc:
            results[table] = ("FAIL", 0, 0)
            log.error(f"  {table} FAILED: {exc}")

    log.info("=" * 50)
    log.info(" Summary")
    log.info("=" * 50)

    all_ok = True
    for table, (status, rows, elapsed) in results.items():
        log.info(f"  [{status}] {table}: {rows} rows ({elapsed}s)")
        if status != "OK":
            all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

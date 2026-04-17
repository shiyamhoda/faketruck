# ============================================================
# AutoParts Data Platform
# Module  : seed_dim_store.py
# Purpose : Seed dim.DimStore - physical and ecommerce channels
# Sprint  : 2
# ============================================================

import os
import sys

if __package__ in (None, ""):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from python.config.db_config import get_db_engine
from python.seed._seed_utils import insert_rows
from python.utils.logger import get_logger

log = get_logger(__name__)

STORES = [
    ("STR-001", "AutoParts Toronto Central", "Retail", "Physical", "Toronto", "ON", "Ontario", "GTA Central", "Kevin Adeyemi", 4500),
    ("STR-002", "AutoParts Mississauga", "Retail", "Physical", "Mississauga", "ON", "Ontario", "GTA West", "Linda Chu", 3800),
    ("STR-003", "AutoParts Scarborough", "Retail", "Physical", "Scarborough", "ON", "Ontario", "GTA East", "Tariq Hussain", 3200),
    ("STR-004", "AutoParts Brampton", "Retail", "Physical", "Brampton", "ON", "Ontario", "GTA West", "Fatima Al-Hassan", 3500),
    ("STR-005", "AutoParts Hamilton", "Retail", "Physical", "Hamilton", "ON", "Ontario", "GTA South", "Brendan Walsh", 2900),
    ("STR-006", "AutoParts Ottawa", "Retail", "Physical", "Ottawa", "ON", "Ontario", "Eastern ON", "Diane Leclair", 3100),
    ("STR-007", "AutoParts Montreal", "Retail", "Physical", "Montreal", "QC", "Quebec", "Montreal Metro", "Jean-Pierre Gagnon", 4000),
    ("STR-008", "AutoParts Calgary", "Retail", "Physical", "Calgary", "AB", "Alberta", "Southern AB", "Marcus Svensson", 3600),
    ("STR-009", "AutoParts Edmonton", "Retail", "Physical", "Edmonton", "AB", "Alberta", "Northern AB", "Priya Sharma", 3300),
    ("STR-010", "AutoParts Vancouver", "Retail", "Physical", "Vancouver", "BC", "British Columbia", "Lower Mainland", "Mei-Lin Wong", 4200),
    ("WH-001", "Distribution Centre - Toronto", "Warehouse", "Physical", "Vaughan", "ON", "Ontario", "GTA North", "Sam Okafor", 25000),
    ("ECOM-001", "AutoParts Online Store", "Ecommerce", "Online", None, None, "National", "National", "Emma Rodriguez", None),
]

INSERT_SQL = """
INSERT INTO dim.DimStore (
    StoreCode, StoreName, StoreType, Channel, Address1, City, Province, PostalCode,
    Country, Phone, ManagerName, OpenDate, CloseDate, SquareFootage, Region,
    District, IsActive
)
VALUES (
    :StoreCode, :StoreName, :StoreType, :Channel, :Address1, :City, :Province, :PostalCode,
    :Country, :Phone, :ManagerName, :OpenDate, :CloseDate, :SquareFootage, :Region,
    :District, :IsActive
)
"""


def build_store_rows() -> list[dict]:
    rows = []
    for store in STORES:
        code, name, store_type, channel, city, province, region, district, manager, square_footage = store
        rows.append({
            "StoreCode": code,
            "StoreName": name,
            "StoreType": store_type,
            "Channel": channel,
            "Address1": None,
            "City": city,
            "Province": province,
            "PostalCode": None,
            "Country": "Canada",
            "Phone": None,
            "ManagerName": manager,
            "OpenDate": "2020-01-01",
            "CloseDate": None,
            "SquareFootage": square_footage,
            "Region": region,
            "District": district,
            "IsActive": 1,
        })
    return rows


def seed(truncate: bool = False) -> int:
    from sqlalchemy import text

    engine = get_db_engine("warehouse")
    with engine.begin() as conn:
        if truncate:
            conn.execute(text("TRUNCATE TABLE dim.DimStore"))
            log.info("dim.DimStore truncated.")
        existing = conn.execute(text("SELECT COUNT(*) FROM dim.DimStore")).scalar()

    if existing and not truncate:
        log.info(f"dim.DimStore already has {existing} rows - skipping.")
        return existing

    rows = build_store_rows()
    insert_rows(engine, INSERT_SQL, rows, chunksize=200)
    log.info(f"dim.DimStore seeded: {len(rows)} rows.")
    return len(rows)


if __name__ == "__main__":
    seed()

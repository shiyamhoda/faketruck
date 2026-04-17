# ============================================================
# AutoParts Data Platform
# Module  : seed_dim_supplier.py
# Purpose : Seed dim.DimSupplier with auto parts distributors
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

SUPPLIERS = [
    ("SUP-001", "Brembo Canada", "OEM", "Carlo Ferri", "carlo@brembocan.ca", "Toronto", "ON", 5, "Net30", 500),
    ("SUP-002", "NGK Distributors CA", "Distributor", "Jenny Wu", "jenny@ngkca.ca", "Vancouver", "BC", 4, "Net30", 300),
    ("SUP-003", "Bosch Auto Parts CA", "OEM", "Frank Muller", "frank@boschca.ca", "Mississauga", "ON", 3, "Net30", 750),
    ("SUP-004", "Ryco Filters", "Distributor", "David Park", "david@rycofilters.ca", "Calgary", "AB", 5, "Net30", 250),
    ("SUP-005", "Gates Rubber CA", "Distributor", "Susan Torres", "susan@gatesrubber.ca", "Brampton", "ON", 4, "Net30", 400),
    ("SUP-006", "Monroe Shocks CA", "Distributor", "Ahmed Nasser", "ahmed@monroeca.ca", "Edmonton", "AB", 6, "Net30", 300),
    ("SUP-007", "Castrol Canada", "Distributor", "Isabelle Roy", "isabelle@castrolca.ca", "Montreal", "QC", 3, "Net30", 600),
    ("SUP-008", "Philips Lighting CA", "OEM", "Tom Nielsen", "tom@philipsca.ca", "Ottawa", "ON", 5, "Net30", 200),
    ("SUP-009", "GMB Bearings CA", "Importer", "Kenji Tanaka", "kenji@gmbca.ca", "Toronto", "ON", 7, "Net45", 400),
    ("SUP-010", "CSF Cooling", "Distributor", "Omar Khalil", "omar@csfcooling.ca", "Vaughan", "ON", 5, "Net30", 350),
]

INSERT_SQL = """
INSERT INTO dim.DimSupplier (
    SupplierCode, SupplierName, SupplierType, ContactName, Email, Phone, Website,
    Address1, City, Province, PostalCode, Country, LeadTimeDays, PaymentTerms,
    CurrencyCode, MinOrderValue, IsActive
)
VALUES (
    :SupplierCode, :SupplierName, :SupplierType, :ContactName, :Email, :Phone, :Website,
    :Address1, :City, :Province, :PostalCode, :Country, :LeadTimeDays, :PaymentTerms,
    :CurrencyCode, :MinOrderValue, :IsActive
)
"""


def build_supplier_rows() -> list[dict]:
    rows = []
    for supplier in SUPPLIERS:
        code, name, supplier_type, contact, email, city, province, lead_days, terms, min_order = supplier
        rows.append({
            "SupplierCode": code,
            "SupplierName": name,
            "SupplierType": supplier_type,
            "ContactName": contact,
            "Email": email,
            "Phone": None,
            "Website": None,
            "Address1": None,
            "City": city,
            "Province": province,
            "PostalCode": None,
            "Country": "Canada",
            "LeadTimeDays": lead_days,
            "PaymentTerms": terms,
            "CurrencyCode": "CAD",
            "MinOrderValue": min_order,
            "IsActive": 1,
        })
    return rows


def seed(truncate: bool = False) -> int:
    from sqlalchemy import text

    engine = get_db_engine("warehouse")
    with engine.begin() as conn:
        if truncate:
            conn.execute(text("TRUNCATE TABLE dim.DimSupplier"))
            log.info("dim.DimSupplier truncated.")
        existing = conn.execute(text("SELECT COUNT(*) FROM dim.DimSupplier")).scalar()

    if existing and not truncate:
        log.info(f"dim.DimSupplier already has {existing} rows - skipping.")
        return existing

    rows = build_supplier_rows()
    insert_rows(engine, INSERT_SQL, rows, chunksize=200)
    log.info(f"dim.DimSupplier seeded: {len(rows)} rows.")
    return len(rows)


if __name__ == "__main__":
    seed()

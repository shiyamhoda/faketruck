# ============================================================
# AutoParts Data Platform
# Module  : seed_dim_product.py
# Purpose : Seed dim.DimProduct with realistic auto parts data
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

PRODUCTS = [
    ("BP-001", "Front Brake Pad Set", "Brakes", "Brake Pads", "Brembo", 42.00, 89.99, "SET"),
    ("BP-002", "Rear Brake Pad Set", "Brakes", "Brake Pads", "Brembo", 38.00, 79.99, "SET"),
    ("BP-003", "Front Brake Pad Set - Economy", "Brakes", "Brake Pads", "AutoStop", 18.00, 39.99, "SET"),
    ("BR-001", "Front Brake Rotor", "Brakes", "Rotors", "DBA", 55.00, 119.99, "EA"),
    ("BR-002", "Rear Brake Rotor", "Brakes", "Rotors", "DBA", 48.00, 99.99, "EA"),
    ("OFL-001", "Engine Oil 5W-30 5L", "Fluids", "Engine Oil", "Castrol", 18.00, 34.99, "EA"),
    ("OFL-002", "Engine Oil 5W-20 5L", "Fluids", "Engine Oil", "Mobil 1", 22.00, 42.99, "EA"),
    ("OFL-003", "Engine Oil 10W-40 4L", "Fluids", "Engine Oil", "Penrite", 14.00, 28.99, "EA"),
    ("OF-001", "Oil Filter", "Filters", "Oil Filters", "Ryco", 4.50, 12.99, "EA"),
    ("OF-002", "Oil Filter - Premium", "Filters", "Oil Filters", "Mann", 7.00, 17.99, "EA"),
    ("AF-001", "Air Filter Panel", "Filters", "Air Filters", "K&N", 12.00, 29.99, "EA"),
    ("AF-002", "Air Filter Round", "Filters", "Air Filters", "Ryco", 8.00, 19.99, "EA"),
    ("CF-001", "Cabin Air Filter", "Filters", "Cabin Filters", "Ryco", 9.00, 22.99, "EA"),
    ("SP-001", "Spark Plug - Iridium", "Ignition", "Spark Plugs", "NGK", 8.50, 18.99, "EA"),
    ("SP-002", "Spark Plug - Copper", "Ignition", "Spark Plugs", "Champion", 3.50, 8.99, "EA"),
    ("SP-003", "Spark Plug - Platinum", "Ignition", "Spark Plugs", "Bosch", 6.00, 14.99, "EA"),
    ("BAT-001", "Battery 12V 60Ah", "Electrical", "Batteries", "Century", 75.00, 159.99, "EA"),
    ("BAT-002", "Battery 12V 70Ah", "Electrical", "Batteries", "Optima", 95.00, 199.99, "EA"),
    ("ALT-001", "Alternator Reman", "Electrical", "Charging", "Bosch", 110.00, 229.99, "EA"),
    ("STR-001", "Starter Motor Reman", "Electrical", "Starting", "Bosch", 95.00, 199.99, "EA"),
    ("BLT-001", "Serpentine Belt", "Belts & Hoses", "Belts", "Gates", 18.00, 39.99, "EA"),
    ("BLT-002", "Timing Belt Kit", "Belts & Hoses", "Belts", "Gates", 65.00, 139.99, "KIT"),
    ("HOS-001", "Radiator Hose Upper", "Belts & Hoses", "Hoses", "Mackay", 12.00, 27.99, "EA"),
    ("HOS-002", "Radiator Hose Lower", "Belts & Hoses", "Hoses", "Mackay", 11.00, 24.99, "EA"),
    ("SUS-001", "Front Shock Absorber", "Suspension", "Shocks", "Monroe", 55.00, 119.99, "EA"),
    ("SUS-002", "Rear Shock Absorber", "Suspension", "Shocks", "Monroe", 48.00, 99.99, "EA"),
    ("SUS-003", "Coil Spring Front", "Suspension", "Springs", "Pedders", 42.00, 89.99, "EA"),
    ("SUS-004", "Sway Bar Link", "Suspension", "Links", "TRW", 14.00, 32.99, "EA"),
    ("STG-001", "Power Steering Fluid 1L", "Fluids", "Steering Fluid", "Penrite", 6.00, 14.99, "EA"),
    ("CLT-001", "Coolant Concentrate 1L", "Fluids", "Coolant", "Nulon", 8.00, 19.99, "EA"),
    ("WW-001", "Windscreen Washer 5L", "Fluids", "Washer Fluid", "Prestone", 5.00, 9.99, "EA"),
    ("WP-001", "Water Pump", "Cooling", "Water Pumps", "GMB", 45.00, 99.99, "EA"),
    ("TH-001", "Thermostat", "Cooling", "Thermostats", "Gates", 12.00, 27.99, "EA"),
    ("RAD-001", "Radiator", "Cooling", "Radiators", "CSF", 120.00, 249.99, "EA"),
    ("LMP-001", "Headlight Bulb H4", "Lighting", "Bulbs", "Philips", 8.00, 18.99, "EA"),
    ("LMP-002", "Headlight Bulb H7", "Lighting", "Bulbs", "Philips", 9.00, 21.99, "EA"),
    ("LMP-003", "LED Headlight Kit", "Lighting", "LED Kits", "Osram", 55.00, 119.99, "KIT"),
    ("WB-001", "Wiper Blade 600mm", "Wipers", "Wiper Blades", "Bosch", 9.00, 22.99, "EA"),
    ("WB-002", "Wiper Blade 450mm", "Wipers", "Wiper Blades", "Bosch", 7.00, 17.99, "EA"),
    ("EX-001", "Exhaust Gasket Set", "Exhaust", "Gaskets", "Permaseal", 14.00, 32.99, "SET"),
]

INSERT_SQL = """
INSERT INTO dim.DimProduct (
    PartNumber, PartDescription, Category, SubCategory, Brand, OEMPartNumber,
    SupplierPartNumber, Barcode, CostPrice, ListPrice, UnitOfMeasure, WeightKg,
    IsOEM, IsHazardous, IsActive, ValidFrom, ValidTo, IsCurrent
)
VALUES (
    :PartNumber, :PartDescription, :Category, :SubCategory, :Brand, :OEMPartNumber,
    :SupplierPartNumber, :Barcode, :CostPrice, :ListPrice, :UnitOfMeasure, :WeightKg,
    :IsOEM, :IsHazardous, :IsActive, :ValidFrom, :ValidTo, :IsCurrent
)
"""


def build_product_rows() -> list[dict]:
    rows = []
    for index, product in enumerate(PRODUCTS, start=1):
        part_number, description, category, sub_category, brand, cost, price, uom = product
        rows.append({
            "PartNumber": part_number,
            "PartDescription": description,
            "Category": category,
            "SubCategory": sub_category,
            "Brand": brand,
            "OEMPartNumber": None,
            "SupplierPartNumber": f"SUP-{part_number}",
            "Barcode": f"6{index:011d}",
            "CostPrice": cost,
            "ListPrice": price,
            "UnitOfMeasure": uom,
            "WeightKg": None,
            "IsOEM": 0,
            "IsHazardous": 0,
            "IsActive": 1,
            "ValidFrom": "2020-01-01",
            "ValidTo": "9999-12-31",
            "IsCurrent": 1,
        })
    return rows


def seed(truncate: bool = False) -> int:
    from sqlalchemy import text

    engine = get_db_engine("warehouse")
    with engine.begin() as conn:
        if truncate:
            conn.execute(text("TRUNCATE TABLE dim.DimProduct"))
            log.info("dim.DimProduct truncated.")
        existing = conn.execute(text("SELECT COUNT(*) FROM dim.DimProduct")).scalar()

    if existing and not truncate:
        log.info(f"dim.DimProduct already has {existing} rows - skipping.")
        return existing

    rows = build_product_rows()
    insert_rows(engine, INSERT_SQL, rows, chunksize=200)
    log.info(f"dim.DimProduct seeded: {len(rows)} rows.")
    return len(rows)


if __name__ == "__main__":
    seed()

# ============================================================
# AutoParts Data Platform
# Module  : seed_dim_customer.py
# Purpose : Seed dim.DimCustomer with mixed retail/trade/fleet
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

CUSTOMERS = [
    ("C001", "Trade", "James", "Okafor", "Okafor Auto Repairs", "james@okaforauto.ca", "Toronto", "ON", "Gold", "Net30"),
    ("C002", "Trade", "Maria", "Santos", "Santos Workshop", "maria@santosws.ca", "Mississauga", "ON", "Silver", "Net30"),
    ("C003", "Fleet", "", "", "City Transit Fleet", "fleet@citytransit.ca", "Toronto", "ON", "Platinum", "Net60"),
    ("C004", "Fleet", "", "", "ProCourier Logistics", "procurement@procourier.ca", "Brampton", "ON", "Platinum", "Net60"),
    ("C005", "Trade", "Ahmed", "Hassan", "Hassan Garage", "ahmed@hassangarage.ca", "Scarborough", "ON", "Silver", "Net30"),
    ("C006", "Retail", "Priya", "Nair", "", "priya.nair@gmail.com", "North York", "ON", "Standard", "COD"),
    ("C007", "Retail", "Liam", "Chen", "", "liam.chen@hotmail.com", "Markham", "ON", "Standard", "COD"),
    ("C008", "Online", "", "", "", "online.cust8@email.com", "Ottawa", "ON", "Standard", "COD"),
    ("C009", "Online", "", "", "", "online.cust9@email.com", "Hamilton", "ON", "Standard", "COD"),
    ("C010", "Trade", "Sophie", "Martin", "Martin Mecanique", "sophie@martinmec.ca", "Montreal", "QC", "Gold", "Net30"),
    ("C011", "Fleet", "", "", "AeroGround Services", "fleet@aeroground.ca", "Calgary", "AB", "Platinum", "Net60"),
    ("C012", "Trade", "Raj", "Patel", "Patel Auto Centre", "raj@patelauto.ca", "Edmonton", "AB", "Silver", "Net30"),
    ("C013", "Retail", "Chloe", "Tremblay", "", "chloe.tremblay@outlook.com", "Quebec City", "QC", "Standard", "COD"),
    ("C014", "Trade", "Dylan", "Park", "Park Performance", "dylan@parkperf.ca", "Vancouver", "BC", "Gold", "Net30"),
    ("C015", "Fleet", "", "", "WestCoast Freight", "accounts@westcoastfreight.ca", "Surrey", "BC", "Platinum", "Net60"),
    ("C016", "Retail", "Nia", "Osei", "", "nia.osei@gmail.com", "Winnipeg", "MB", "Standard", "COD"),
    ("C017", "Online", "", "", "", "online.cust17@email.com", "Halifax", "NS", "Standard", "COD"),
    ("C018", "Trade", "Marco", "Russo", "Russo Collision", "marco@russocollision.ca", "Windsor", "ON", "Silver", "Net30"),
    ("C019", "Fleet", "", "", "MuniWorks Infrastructure", "fleet@muniworks.ca", "London", "ON", "Platinum", "Net60"),
    ("C020", "Retail", "Aisha", "Diallo", "", "aisha.diallo@gmail.com", "Kitchener", "ON", "Standard", "COD"),
]

INSERT_SQL = """
INSERT INTO dim.DimCustomer (
    CustomerCode, CustomerType, FirstName, LastName, CompanyName, Email, Phone,
    Address1, City, Province, PostalCode, Country, PriceTier, CreditLimit,
    PaymentTerms, IsActive, ValidFrom, ValidTo, IsCurrent
)
VALUES (
    :CustomerCode, :CustomerType, :FirstName, :LastName, :CompanyName, :Email, :Phone,
    :Address1, :City, :Province, :PostalCode, :Country, :PriceTier, :CreditLimit,
    :PaymentTerms, :IsActive, :ValidFrom, :ValidTo, :IsCurrent
)
"""


def build_customer_rows() -> list[dict]:
    rows = []
    for customer in CUSTOMERS:
        code, customer_type, first_name, last_name, company_name, email, city, province, tier, terms = customer
        rows.append({
            "CustomerCode": code,
            "CustomerType": customer_type,
            "FirstName": first_name or None,
            "LastName": last_name or None,
            "CompanyName": company_name or None,
            "Email": email or None,
            "Phone": None,
            "Address1": None,
            "City": city,
            "Province": province,
            "PostalCode": None,
            "Country": "Canada",
            "PriceTier": tier,
            "CreditLimit": {"Standard": None, "Silver": 5000, "Gold": 15000, "Platinum": 50000}[tier],
            "PaymentTerms": terms,
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
            conn.execute(text("DELETE FROM dim.DimCustomer WHERE CustomerKey > 0"))
            log.info("dim.DimCustomer seed rows cleared (unknown member retained).")
        existing = conn.execute(text("SELECT COUNT(*) FROM dim.DimCustomer WHERE CustomerKey > 0")).scalar()

    if existing and not truncate:
        log.info(f"dim.DimCustomer already has {existing} seed rows - skipping.")
        return existing

    rows = build_customer_rows()
    insert_rows(engine, INSERT_SQL, rows, chunksize=200)
    log.info(f"dim.DimCustomer seeded: {len(rows)} rows.")
    return len(rows)


if __name__ == "__main__":
    seed()

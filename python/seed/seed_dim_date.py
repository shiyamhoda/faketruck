# ============================================================
# AutoParts Data Platform
# Module  : seed_dim_date.py
# Purpose : Populate dim.DimDate for a configurable date range
# Sprint  : 2
# ============================================================

import os
import sys
from datetime import date, timedelta

if __package__ in (None, ""):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from python.config.db_config import get_db_engine
from python.seed._seed_utils import insert_rows
from python.utils.logger import get_logger

log = get_logger(__name__)

START_DATE = date(2020, 1, 1)
END_DATE = date(2026, 12, 31)

PUBLIC_HOLIDAYS = {
    "New Year's Day": [(year, 1, 1) for year in range(2020, 2027)],
    "Canada Day": [(year, 7, 1) for year in range(2020, 2027)],
    "Christmas Day": [(year, 12, 25) for year in range(2020, 2027)],
    "Boxing Day": [(year, 12, 26) for year in range(2020, 2027)],
    "Victoria Day": [(2020, 5, 18), (2021, 5, 24), (2022, 5, 23), (2023, 5, 22), (2024, 5, 20), (2025, 5, 19), (2026, 5, 18)],
    "Labour Day": [(2020, 9, 7), (2021, 9, 6), (2022, 9, 5), (2023, 9, 4), (2024, 9, 2), (2025, 9, 1), (2026, 9, 7)],
    "Thanksgiving (CA)": [(2020, 10, 12), (2021, 10, 11), (2022, 10, 10), (2023, 10, 9), (2024, 10, 14), (2025, 10, 13), (2026, 10, 12)],
    "Remembrance Day": [(year, 11, 11) for year in range(2020, 2027)],
}

INSERT_SQL = """
INSERT INTO dim.DimDate (
    DateKey, FullDate, Year, Quarter, QuarterName, Month, MonthName, MonthShort,
    Week, DayOfMonth, DayOfWeek, DayName, DayShort, IsWeekend, IsPublicHoliday,
    HolidayName, FiscalYear, FiscalQuarter, FiscalMonth, YearMonth, YearQuarter
)
VALUES (
    :DateKey, :FullDate, :Year, :Quarter, :QuarterName, :Month, :MonthName, :MonthShort,
    :Week, :DayOfMonth, :DayOfWeek, :DayName, :DayShort, :IsWeekend, :IsPublicHoliday,
    :HolidayName, :FiscalYear, :FiscalQuarter, :FiscalMonth, :YearMonth, :YearQuarter
)
"""


def _build_holiday_map() -> dict[date, str]:
    holiday_map = {}
    for name, holiday_dates in PUBLIC_HOLIDAYS.items():
        for year, month, day in holiday_dates:
            holiday_map[date(year, month, day)] = name
    return holiday_map


def _fiscal_year(value: date) -> tuple[str, int, int]:
    if value.month >= 4:
        fy_start, fy_end = value.year, value.year + 1
        fiscal_month = value.month - 3
    else:
        fy_start, fy_end = value.year - 1, value.year
        fiscal_month = value.month + 9

    fiscal_label = f"FY{fy_start}-{str(fy_end)[-2:]}"
    fiscal_quarter = (fiscal_month - 1) // 3 + 1
    return fiscal_label, fiscal_quarter, fiscal_month


def build_date_rows(start: date, end: date) -> list[dict]:
    holiday_map = _build_holiday_map()
    rows = []
    current = start

    while current <= end:
        day_of_week = current.isoweekday()
        holiday_name = holiday_map.get(current)
        fiscal_year, fiscal_quarter, fiscal_month = _fiscal_year(current)
        rows.append({
            "DateKey": int(current.strftime("%Y%m%d")),
            "FullDate": current,
            "Year": current.year,
            "Quarter": (current.month - 1) // 3 + 1,
            "QuarterName": f"Q{(current.month - 1) // 3 + 1}",
            "Month": current.month,
            "MonthName": current.strftime("%B"),
            "MonthShort": current.strftime("%b"),
            "Week": current.isocalendar()[1],
            "DayOfMonth": current.day,
            "DayOfWeek": day_of_week,
            "DayName": current.strftime("%A"),
            "DayShort": current.strftime("%a"),
            "IsWeekend": int(day_of_week >= 6),
            "IsPublicHoliday": int(holiday_name is not None),
            "HolidayName": holiday_name,
            "FiscalYear": fiscal_year,
            "FiscalQuarter": fiscal_quarter,
            "FiscalMonth": fiscal_month,
            "YearMonth": int(current.strftime("%Y%m")),
            "YearQuarter": f"{current.year}-Q{(current.month - 1) // 3 + 1}",
        })
        current += timedelta(days=1)

    return rows


def seed(truncate: bool = False) -> int:
    from sqlalchemy import text

    engine = get_db_engine("warehouse")
    with engine.begin() as conn:
        if truncate:
            conn.execute(text("TRUNCATE TABLE dim.DimDate"))
            log.info("dim.DimDate truncated.")
        existing = conn.execute(text("SELECT COUNT(*) FROM dim.DimDate")).scalar()

    if existing and not truncate:
        log.info(f"dim.DimDate already has {existing} rows - skipping seed.")
        return existing

    log.info(f"Building date range {START_DATE} to {END_DATE}...")
    rows = build_date_rows(START_DATE, END_DATE)
    insert_rows(engine, INSERT_SQL, rows, chunksize=500)
    log.info(f"dim.DimDate seeded: {len(rows)} rows.")
    return len(rows)


if __name__ == "__main__":
    seed()

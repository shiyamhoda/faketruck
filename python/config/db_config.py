import os

DB_CONFIG = {
    "staging": {
        "server": r"SHIYAMSPERSONAL\SQLEXPRESS",
        "database": os.getenv("DB_STAGING", "AutoParts_Staging"),
        "driver": "ODBC Driver 17 for SQL Server",
        "trusted": True,
    },
    "ods": {
        "server": r"SHIYAMSPERSONAL\SQLEXPRESS",
        "database": os.getenv("DB_ODS", "AutoParts_ODS"),
        "driver": "ODBC Driver 17 for SQL Server",
        "trusted": True,
    },
    "warehouse": {
        "server": r"SHIYAMSPERSONAL\SQLEXPRESS",
        "database": os.getenv("DB_DW", "AutoParts_DW"),
        "driver": "ODBC Driver 17 for SQL Server",
        "trusted": True,
    },
}


def get_db_engine(layer: str):
    """Return a SQLAlchemy engine for the given layer."""

    from sqlalchemy import create_engine
    from sqlalchemy.engine import URL

    if layer not in DB_CONFIG:
        raise ValueError(f"Invalid layer: {layer}")

    cfg = DB_CONFIG[layer]

    # Base query params
    query = {
        "driver": cfg["driver"],
        "TrustServerCertificate": "yes",
    }

    if cfg["trusted"]:
        query["Trusted_Connection"] = "yes"

        connection_url = URL.create(
            "mssql+pyodbc",
            host=cfg["server"],
            database=cfg["database"],
            query=query,
        )

    else:
        connection_url = URL.create(
            "mssql+pyodbc",
            host=cfg["server"],
            database=cfg["database"],
            username=cfg["username"],
            password=cfg["password"],
            query=query,
        )

    return create_engine(connection_url)

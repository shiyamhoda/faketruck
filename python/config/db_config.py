# ============================================================
# AutoParts Data Platform
# Module  : db_config.py
# Purpose : Central database connection config
# Sprint  : 1
# ============================================================

import os

# Override any value with environment variables for CI/CD
DB_CONFIG = {
    "staging": {
        "server":   os.getenv("DB_SERVER",   "ShiyamsPersonal\SQLEXPRESS"),
        "database": os.getenv("DB_STAGING",  "AutoParts_Staging"),
        "driver":   "ODBC Driver 17 for SQL Server",
        "trusted":  True,   # Windows auth; set False for SQL auth
        # "username": os.getenv("DB_USER", ""),
        # "password": os.getenv("DB_PASS", ""),
    },
    "ods": {
        "server":   os.getenv("DB_SERVER", "ShiyamsPersonal\SQLEXPRESS"),
        "database": os.getenv("DB_ODS",    "AutoParts_ODS"),
        "driver":   "ODBC Driver 17 for SQL Server",
        "trusted":  True,
    },
    "warehouse": {
        "server":   os.getenv("DB_SERVER", "ShiyamsPersonal\SQLEXPRESS"),
        "database": os.getenv("DB_DW",     "AutoParts_DW"),
        "driver":   "ODBC Driver 17 for SQL Server",
        "trusted":  True,
    },
}

def get_connection_string(layer: str) -> str:
    """Return a pyodbc connection string for the given layer."""
    cfg = DB_CONFIG[layer]
    if cfg["trusted"]:
        return (
            f"DRIVER={{{cfg['driver']}}};"
            f"SERVER={cfg['server']};"
            f"DATABASE={cfg['database']};"
            "Trusted_Connection=yes;"
        )
    return (
        f"DRIVER={{{cfg['driver']}}};"
        f"SERVER={cfg['server']};"
        f"DATABASE={cfg['database']};"
        f"UID={cfg['username']};"
        f"PWD={cfg['password']};"
    )
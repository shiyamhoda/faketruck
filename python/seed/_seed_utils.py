import os
import sys
from itertools import islice
from typing import Iterable


if __package__ in (None, ""):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


def chunked(rows: list[dict], size: int) -> Iterable[list[dict]]:
    iterator = iter(rows)
    while True:
        batch = list(islice(iterator, size))
        if not batch:
            return
        yield batch


def insert_rows(engine, insert_sql: str, rows: list[dict], chunksize: int = 500) -> int:
    from sqlalchemy import text

    if not rows:
        return 0

    statement = text(insert_sql)
    with engine.begin() as conn:
        for batch in chunked(rows, chunksize):
            conn.execute(statement, batch)

    return len(rows)

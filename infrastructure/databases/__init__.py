from contextlib import contextmanager
from typing import List

from .database import SessionLocalPG


def get_db_pg():
    db = SessionLocalPG()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_pg_conn():
    db = SessionLocalPG()
    try:
        yield db
    finally:
        db.close()


def alchemy_to_dict(query):
    if query is None:
        return None
    if isinstance(query, List):
        return [dict(item) for item in query]
    return dict(query)

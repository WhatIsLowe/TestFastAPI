from uuid import UUID
from sqlalchemy import text
from sqlalchemy.orm import Session

from . import sql_queries
from infrastructure.databases import alchemy_to_dict


def add_proxy6_api_key(pg: Session, user_uuid: UUID, api_key: str):
    return pg.execute(
        text(sql_queries.ADD_PROXY6_API_KEY),
        {'user_id': user_uuid, 'api_key': api_key}
    ).fetchone()


def get_proxy6_api_key(pg: Session, user_uuid: UUID):
    return pg.execute(
        text(sql_queries.GET_PROXY6_API_KEY),
        {'user_id': user_uuid}
    ).fetchone()

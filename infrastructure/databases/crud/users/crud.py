from sqlalchemy import text
from sqlalchemy.orm import Session
from uuid import UUID

from infrastructure.databases import alchemy_to_dict
from . import sql_queries


def get_user_data_by_session_uuid(pg: Session, session_uuid: str) -> dict | None:
    return alchemy_to_dict(
        pg.execute(
            text(sql_queries.GET_USER_INFO_BY_SESSION),
            {'session_uuid': session_uuid}
        ).mappings().first()
    )


def get_session_by_uuid(pg: Session, session_uuid: UUID) -> dict | None:
    return alchemy_to_dict(
        pg.execute(
            text(sql_queries.GET_SESSION_BY_UUID),
            {'session_uuid': session_uuid}
        ).mappings().first()
    )

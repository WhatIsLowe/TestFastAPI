from uuid import uuid4, UUID
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel

from infrastructure.databases import alchemy_to_dict
from . import sql_queries


def get_user_by_username(pg: Session, username: str) -> dict | None:
    """Получает хэшированный пароль из БД"""

    return alchemy_to_dict(
        pg.execute(
            text(sql_queries.GET_USER_BY_USERNAME),
            {'username': username}
        ).mappings().first()
    )


def is_existing_username(pg: Session, username: str) -> bool:
    res = pg.execute(
        text(sql_queries.USERNAME_EXISTS),
        {'username': username}
    ).fetchone()
    if res:
        return True
    return False


class RegisterUserData(BaseModel):
    username: str
    password: str


def register_user(pg: Session, user_data: dict[str, str]) -> UUID:
    result = alchemy_to_dict(
        pg.execute(
            text(sql_queries.REGISTER_USER),
            {"username": user_data['username'], "password": user_data['password']},
        ).mappings().first()
    )
    pg.commit()
    print(result)
    return result


def get_user_by_uuid(pg: Session, user_uuid: str):
    return alchemy_to_dict(
        pg.execute(
            text(sql_queries.GET_USER_BY_UUID),
            {'uuid': user_uuid}
        ).mappings().first()
    )

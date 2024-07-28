from uuid import UUID

from fastapi import Security, HTTPException, Request, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from starlette import status
from sqlalchemy.orm import Session

from infrastructure.databases import get_db_pg
from infrastructure.databases.crud.users import crud as users_crud
from tools.crypt import decrypt
from tools.validation import is_valid_api_key

Authorization = APIKeyHeader(name='Authorization', auto_error=False)


class UserInfo(BaseModel):
    uuid: UUID
    username: str


def login_request(
        request: Request,
        authorization: str = Depends(Authorization),
        pg: Session = Depends(get_db_pg)
) -> UserInfo:
    if authorization:
        try:
            user_data = users_crud.get_user_data_by_session_uuid(pg, authorization)
            if not user_data:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User does not exist')
            return UserInfo(**user_data)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')


def is_valid_session(pg: Session, session_id: UUID):
    session_data = users_crud.get_session_by_uuid(pg, session_id)
    if not session_data:
        return False

    return True

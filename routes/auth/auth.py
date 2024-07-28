import logging
from pydantic import BaseModel

from fastapi import HTTPException, APIRouter, Request, Depends

from sqlalchemy.orm import Session

from tools.limiter import limiter_ip
from tools.crypt import encrypt_password
from infrastructure.databases import get_db_pg
from infrastructure.databases.crud.auth import crud as auth_crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

request_limiter = "2/second"


class LoginModel(BaseModel):
    username: str
    password: str


@router.post("/login")
@limiter_ip.limit(request_limiter)
async def login(request: Request, data: LoginModel, pg: Session = Depends(get_db_pg)):
    logger.info(f"Login attempt: {data.username}")

    if not data.username.strip() or not data.password.strip():
        logger.warning("Empty username or password")
        raise HTTPException(status_code=400, detail="Empty username or password!")

    db_user = auth_crud.get_user_by_username(pg, data.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password!")

    encrypted_password = encrypt_password(data.password)
    if encrypted_password == db_user["password"]:
        return {"status": "ok", "uuid": db_user["id"]}

    raise HTTPException(status_code=400, detail="Invalid username or password!")


class RegisterModel(BaseModel):
    username: str
    password: str


@router.post("/register")
@limiter_ip.limit(request_limiter)
async def register(request: Request, data: RegisterModel, pg: Session = Depends(get_db_pg)):
    logger.info(f"Register attempt: {data.username}")

    if not data.username or (len(data.username.strip()) < 6):
        raise HTTPException(status_code=400, detail="Username is too short!")

    if auth_crud.is_existing_username(pg, data.username):
        raise HTTPException(status_code=400, detail="Username is taken!")

    user_data = {"username": data.username, "password": encrypt_password(data.password)}

    user_id = auth_crud.register_user(pg, user_data)
    if user_id:
        return {"status": "ok", "uuid": user_id}

    raise HTTPException(status_code=400, detail="WTF...")


@router.post("/get_user")
@limiter_ip.limit(request_limiter)
async def get_user(request: Request, user_id: str, pg=Depends(get_db_pg)):
    logger.info(f"Get user attempt: {user_id}")
    if not user_id or (len(user_id.strip()) != 36):
        raise HTTPException(status_code=400, detail="Invalid user_id!")

    user_data = auth_crud.get_user_by_uuid(pg, user_id)

    if not user_data:
        raise HTTPException(status_code=404, detail="User not found!")

    return {"status": "ok", "user_data": user_data}

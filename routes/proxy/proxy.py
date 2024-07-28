from fastapi import APIRouter, Depends, HTTPException, status, Request
import requests
import typing as T

from pydantic import BaseModel
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session

from .models import (
    APIKeyError,
    ProxyNotFoundError,
    ProxyData,
    ChangeProxyTypeModel
)
from ..auth import login_request
from tools.limiter import limiter_ip
from tools.validation import is_valid_api_key
from infrastructure.databases import get_db_pg
from infrastructure.databases.crud.proxy import crud as proxy_crud

router = APIRouter(prefix="/proxy", tags=['proxy'])
request_limiter = "2/second"


class ProxyNoAPIKeyError(HTTPException):
    def __init__(self, detail: str = "No Proxy6 API key found."):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


@router.get("/proxy6",
            response_model=T.List[ProxyData],
            responses={
                400: {"model": APIKeyError},
                404: {"model": ProxyNotFoundError}
            })
@limiter_ip.limit(request_limiter)
async def get_proxy6(request: Request, user_info=Depends(login_request), pg: Session = Depends(get_db_pg)):
    proxy_api_key = proxy_crud.get_proxy6_api_key(pg, user_info.uuid)
    if not proxy_api_key:
        raise ProxyNoAPIKeyError()

    url = f'https://proxy6.net/api/{proxy_api_key}/getproxy'
    response = requests.get(url)
    print(response.json())
    if response.status_code != 200 or response.json()["status"] == 'no':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.text)

    response = response.json()

    if len(response['list']) == 0:
        raise HTTPException(404, detail="No proxy available")

    print(response)

    return [
        ProxyData(
            id=proxy['id'],
            host=proxy['host'],
            port=int(proxy['port']),
            username=proxy['user'],
            password=proxy['pass'],
            type=proxy['type'],
            time_end=int(proxy['unixtime_end']),
            active=True if proxy['active'] == "1" else False,
        ) for proxy in response['list'].values()
    ]


@router.post("/set_type")
@limiter_ip.limit(request_limiter)
async def set_type(request: Request, new_type: ChangeProxyTypeModel, user_info=Depends(login_request),
                   pg: Session = Depends(get_db_pg)):
    api_key = proxy_crud.get_proxy6_api_key(pg, user_info.uuid)
    if not api_key:
        raise ProxyNoAPIKeyError()

    ids_str = ",".join(str(id) for id in new_type.ids)
    url = f"https://proxy6.net/api/{api_key}/settype?ids={ids_str}&type={new_type.type.value}"
    print(url)
    response = requests.get(url)

    if response.status_code != 200 or response.json()["status"] == 'no':
        raise HTTPException(response.status_code, detail=response.text)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})


class ProxyApiKeyModel(BaseModel):
    api_key: str


# def is_valid_proxy6_api_key(api_key: str) -> bool:
#     url = f'https://proxy6.net/api/{api_key}/getproxy'
#     response = requests.get(url)
#     if response.status_code != 200 or response.json()["status"] == 'no':
#         return False
#     return True


@router.post("/add_api_key")
@limiter_ip.limit(request_limiter)
async def add_proxy_api_key(request: Request, data: ProxyApiKeyModel, user_info=Depends(login_request),
                            pg: Session = Depends(get_db_pg)):
    if not data.api_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No Proxy6 API key provided.")

    if not is_valid_api_key(data.api_key):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Proxy6 API key provided.")

    proxy_api_key_id = proxy_crud.add_proxy6_api_key(pg, user_info.uuid, data.api_key)
    if not proxy_api_key_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB ERROR")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok", "proxy_api_key_id": proxy_api_key_id})

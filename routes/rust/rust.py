from enum import IntEnum

from fastapi import APIRouter, Depends, status, Request

from starlette.responses import JSONResponse
from sqlalchemy.orm import Session

from infrastructure.databases import get_db_pg
from infrastructure.databases.crud.rust import crud as crud_rust

import rust_tree_builder as rtb

from envparse import env

env.read_envfile()

router = APIRouter(prefix="/rust", tags=["rust"])
request_limiter = "2/second"


@router.get("/test_python", status_code=status.HTTP_204_NO_CONTENT)
async def test_python(request: Request):
    pass


class LimitModel(IntEnum):
    NONE = 0
    TEN = 10
    HUNDRED = 100
    THOUSAND = 1000
    LITTLE = 10000
    MANY = 100000
    HUGE = 1000000


@router.get("/test_rust")
async def test_rust(request: Request, limit: LimitModel, pg: Session = Depends(get_db_pg)):
    raw_data = await crud_rust.get_all_nodes(pg, limit)
    tree = rtb.build_tree(raw_data)

    tree_dict = [node.to_dict() for node in tree]
    return JSONResponse(content=tree_dict, media_type="application/json")

from sqlalchemy import text
from sqlalchemy.orm import Session

from infrastructure.databases import alchemy_to_dict
from . import sql_queries


async def get_all_nodes(db: Session, limit) -> list[dict]:
    if not limit.NONE:
        res = alchemy_to_dict(
            db.execute(text(sql_queries.GET_ALL_NODES_LIMITED), {"limit": limit.value}).mappings().all()
        )
    else:
        res = alchemy_to_dict(db.execute(text(sql_queries.GET_ALL_NODES)).mappings().all())
    return res

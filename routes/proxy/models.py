from enum import Enum
import typing as T

from pydantic import BaseModel


class ProxyType(Enum):
    HTTP = "http"
    SOCKS = "socks"


class APIKeyError(BaseModel):
    detail: str = "API key is required"


class ProxyNotFoundError(BaseModel):
    detail: str = "No proxy available"


class ProxyData(BaseModel):
    id: int
    host: str
    port: int
    username: str
    password: str
    type: ProxyType
    time_end: int
    active: bool


class ChangeProxyTypeModel(BaseModel):
    ids: T.List[int]
    type: ProxyType

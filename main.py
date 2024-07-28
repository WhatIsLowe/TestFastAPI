from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
import logging

from envparse import env

from routes.auth.auth import router as auth_router
from routes.proxy.proxy import router as proxy_router
from routes.websocket.websocket import router as websocket_router
from routes.kandinsky.kandinsky import router as kandinsky_router
from routes.rust.rust import router as rust_router

from tools.limiter import rate_limit_exceeded_handler

env.read_envfile()

app = FastAPI(debug=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Обработчик префлайт-запросов
@app.options("/{rest_of_path:path}", include_in_schema=False)
async def preflight_handler(request: Request) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={"message": "Preflight request successful"},
        headers={
            "Access-Control-Allow-Origin": "http://localhost:4200",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(RateLimitExceeded, handler=rate_limit_exceeded_handler)

app.include_router(auth_router)
app.include_router(proxy_router)
app.include_router(websocket_router)
app.include_router(kandinsky_router)
app.include_router(rust_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )

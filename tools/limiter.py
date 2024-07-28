from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_ipaddr

limiter_ip = Limiter(key_func=get_ipaddr)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    response = JSONResponse({"error": f"Rate Limit Exceeded: {exc.detail}"}, status_code=429)
    return response

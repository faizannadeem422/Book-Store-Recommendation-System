from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)
        
        duration = time.time() - start_time
        print(f"[{request.method}] {request.url} took {duration:.4f}s")
        return response

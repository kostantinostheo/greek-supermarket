import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from limits import parse
from limits.storage import MemoryStorage
from limits.strategies import FixedWindowRateLimiter
from starlette.exceptions import HTTPException as StarletteHTTPException

from routes.routes import router as api_router

limit = parse("100 per 15 minutes")  # 15 minutes, limit 100
limiter = FixedWindowRateLimiter(MemoryStorage())

PORT = 8000

app = FastAPI(
    title="Greek Market API",
    version="0.0.1",
    description="API for fetching and processing product data from the Greek market. Supports pagination, sorting, and filtering of products.",
    docs_url="/api-docs",
    redoc_url=None,
)


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    client = request.client.host if request.client else "unknown"
    if not limiter.hit(limit, client):
        return JSONResponse(
            {"error": "Too many requests, please try again later."}, status_code=429
        )
    return await call_next(request)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    print(f"API running at http://localhost:{PORT}")
    uvicorn.run("server:app", host="127.0.0.1", port=PORT, reload=True)

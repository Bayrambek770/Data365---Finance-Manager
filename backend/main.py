import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routers import users, overview, transactions, categories, analytics, budgets, bot

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Xisob Finance API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("%s %s", request.method, request.url.path)
    response = await call_next(request)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "code": "INTERNAL_ERROR"},
    )


PREFIX = "/api/v1"

app.include_router(users.router, prefix=PREFIX)
app.include_router(overview.router, prefix=PREFIX)
app.include_router(transactions.router, prefix=PREFIX)
app.include_router(categories.router, prefix=PREFIX)
app.include_router(analytics.router, prefix=PREFIX)
app.include_router(budgets.router, prefix=PREFIX)
app.include_router(bot.router, prefix=PREFIX)


@app.get("/health")
def health():
    return {"status": "ok"}

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, Response
import redis.asyncio as redis
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Limiter, Rate

from core.config import Config as cfg
from core.rate_limit import RedisRateLimitBucketFactory
from middleware import require_middleware
from error import require_error
from routes.humanizer_route import humanize_router
from routes.payment_route import payment_router
from routes.user_route import user_router

version = "v1"


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_connection = redis.from_url(
        cfg.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    rate = Rate(
        limit=cfg.RATE_LIMIT_REQUESTS,
        interval=cfg.RATE_LIMIT_WINDOW_SECONDS * 1000,
    )
    bucket_factory = RedisRateLimitBucketFactory(
        rates=[rate],
        redis=redis_connection,
        key_prefix="altohuman:rate-limit",
    )
    app.state.rate_limiter = RateLimiter(
        limiter=Limiter(bucket_factory),
        blocking=False,
    )
    yield
    bucket_factory.close()
    await redis_connection.aclose()


async def rate_limit(request: Request, response: Response):
    return await request.app.state.rate_limiter(request, response)


app = FastAPI(
    title="Altohuman-server",
    description="Altohuman-server backend",
    version=version,
    docs_url=f"/api/{version}/docs",
    redoc_url=f"/api/{version}/redoc",
    lifespan=lifespan,
)

require_middleware(app)
require_error(app)


app.include_router(
    user_router,
    prefix=f"/api/{version}/user",
    tags=["user"],
    dependencies=[Depends(rate_limit)],
)
app.include_router(
    payment_router,
    prefix=f"/api/{version}/payment",
    tags=["payment"],
    dependencies=[Depends(rate_limit)],
)
app.include_router(
    humanize_router,
    prefix=f"/api/{version}/humanize",
    tags=["humanizer"],
    dependencies=[Depends(rate_limit)],
)

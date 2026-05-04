from fastapi import FastAPI

from middleware import require_middleware
from error import require_error
from routes.user_route import user_router

version = "v1"

app = FastAPI(
    title="Altohuman-server",
    description="Altohuman-server backend",
    version=version,
    docs_url=f"/api/{version}/docs",
    redoc_url=f"/api/{version}/redoc",
)

require_middleware(app)
require_error(app)


app.include_router(user_router, prefix=f"/api/{version}/user", tags=["user"])

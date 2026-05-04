from fastapi import FastAPI

from middleware import require_middleware

version = "v1"

app = FastAPI(
    title="Altohuman-server",
    description="Altohuman-server backend",
    version=version,
    docs_url=f"/api/{version}/docs",
    redoc_url=f"/api/{version}/redoc",
)

require_middleware(app)

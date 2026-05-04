from fastapi import FastAPI

version = "v1"

app = FastAPI(
    title="Altohuman-server",
    description="Altohuman-server backend",
    version=version,
    docs_url=f"/api/{version}/docs",
    redoc_url=f"/api/{version}/redoc",
)

import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

logging = logging.getLogger("uvicorn.access")
logging.disabled = True


def require_middleware(app: FastAPI):
    # LOGGING
    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)
        processing_time = time.time() - start_time

        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed after {processing_time}s"

        print(message)
        return response

    # TRUSTED_HOST
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        # No trailing slash on origin
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        # Instead of ["*"], try listing them specifically to satisfy strict browsers
        allow_methods=["*"],
        allow_headers=["*"],
    )

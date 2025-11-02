from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware

# Ensure WeasyPrint native libs are discoverable on macOS/Homebrew BEFORE importing routers
os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib:/usr/local/lib")

from .routers import compare, export


def create_app() -> FastAPI:
    app = FastAPI(title="Erik's Super Compare API", version="0.1.0", debug=True)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(compare.router)
    app.include_router(export.router)

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()



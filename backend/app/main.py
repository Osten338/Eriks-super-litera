from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import compare, export


def create_app() -> FastAPI:
    app = FastAPI(title="Erik's Super Compare API", version="0.1.0")

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



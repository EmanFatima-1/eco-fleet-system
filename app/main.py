# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.responses import FileResponse
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, engine
from app.domain import models  # Ensure models are loaded for Base.metadata
from app.interfaces.controllers import router as api_router

# Create database tables on startup / import
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_TITLE,
    version=settings.PROJECT_VERSION,
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API endpoints router
app.include_router(api_router)


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)


@app.get("/", response_class=FileResponse)
def read_root():
    return FileResponse("static/index.html")

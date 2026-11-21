import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import init_db
from .seed_data import seed_database
from .routes import complaints, ai_triage, stats

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema & seed sample data
    init_db()
    seed_database()
    yield

app = FastAPI(
    title="CivicResolve API",
    description="AI-Powered Citizen Grievance Management and Resolution Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware (allows React frontend on any port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(complaints.router)
app.include_router(ai_triage.router)
app.include_router(stats.router)

# Directory paths
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BACKEND_DIR)
UPLOADS_DIR = os.path.join(BACKEND_DIR, "uploads")
STATIC_DIR = os.path.join(ROOT_DIR, "static")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Mount uploads static folder
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Serve embedded frontend SPA if static folder contains index.html
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "status": "online",
        "message": "CivicResolve API is running. Visit /docs for Swagger API documentation."
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": "CivicResolve",
        "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY"))
    }

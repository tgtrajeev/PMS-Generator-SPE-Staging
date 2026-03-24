"""
FastAPI application for PMS Generator.
Replaces Flask app.py with async endpoints, Pydantic validation, and auto-docs.
"""

import os
import sys
import traceback

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from db.database import engine, Base, run_migrations
from db.seed import seed_all

from api.routers import materials, calculations, components, pms, specs, validation

# Create tables, run migrations, and seed — all wrapped so startup never crashes
try:
    Base.metadata.create_all(bind=engine)
except Exception as _e:
    print(f"[startup] create_all failed: {_e}", flush=True)

try:
    run_migrations()
except Exception as _e:
    print(f"[startup] run_migrations failed: {_e}", flush=True)

seed_all()  # already has its own internal try/except

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="PMS Generator API",
    description="Piping Material Specification Generator - ASME B31.3 compliant",
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory=os.path.join(PROJECT_ROOT, "static")), name="static")

# Templates
templates = Jinja2Templates(directory=os.path.join(PROJECT_ROOT, "templates"))

# Include routers
app.include_router(materials.router, prefix="/api", tags=["Materials"])
app.include_router(calculations.router, prefix="/api", tags=["Calculations"])
app.include_router(components.router, prefix="/api", tags=["Components"])
app.include_router(pms.router, prefix="/api", tags=["PMS Generation"])
app.include_router(specs.router, prefix="/api", tags=["Saved Specs"])
app.include_router(validation.router, prefix="/api", tags=["Validation"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    print(f"[UNHANDLED ERROR] {request.method} {request.url}\n{tb}", flush=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": tb},
    )


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

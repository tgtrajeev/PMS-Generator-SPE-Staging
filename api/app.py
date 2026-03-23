"""
FastAPI application for PMS Generator.
Replaces Flask app.py with async endpoints, Pydantic validation, and auto-docs.
"""

import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from db.database import engine, Base, run_migrations
from db.seed import seed_all

from api.routers import materials, calculations, components, pms, specs, validation

# Create tables
Base.metadata.create_all(bind=engine)

# Run column migrations (adds new columns to existing DB without data loss)
run_migrations()

# Seed database on first run
seed_all()

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


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

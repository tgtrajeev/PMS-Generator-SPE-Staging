#!/usr/bin/env python3
"""
PMS Generator - FastAPI Web Application
Serves the Piping Material Specification generator on port 8080.
"""

import uvicorn

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  PMS Generator v2.0 - FastAPI Web Interface")
    print("  Open http://localhost:8080 in your browser")
    print("  API Docs: http://localhost:8080/docs")
    print("=" * 60 + "\n")
    uvicorn.run("api.app:app", host="0.0.0.0", port=8080, reload=True)

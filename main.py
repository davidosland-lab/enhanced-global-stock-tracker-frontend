#!/usr/bin/env python3
"""
Entry point for Railway deployment
Redirects to the backend FastAPI app
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import and run the app
if __name__ == "__main__":
    os.chdir('backend')
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
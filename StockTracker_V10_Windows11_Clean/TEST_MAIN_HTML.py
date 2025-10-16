"""
Simple test to verify main backend can serve HTML
"""

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Serve index.html"""
    if os.path.exists("index.html"):
        print("Serving index.html")
        return FileResponse("index.html", media_type="text/html")
    else:
        print(f"index.html not found in {os.getcwd()}")
        print(f"Files in directory: {os.listdir('.')}")
        return {"error": f"index.html not found in {os.getcwd()}"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "main_backend"}

if __name__ == "__main__":
    print("="*60)
    print("Test Main Backend - Serving HTML")
    print("="*60)
    print(f"Current directory: {os.getcwd()}")
    print(f"Files: {os.listdir('.')}")
    print()
    print("Starting server on http://localhost:8000")
    print("Open browser to http://localhost:8000")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
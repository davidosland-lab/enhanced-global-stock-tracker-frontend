#!/usr/bin/env python3
"""
Webhook endpoint for automatic prompt capture
Can be integrated with various services to automatically capture prompts
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import os
import sys

# Add the prompts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from prompt_capture_system import PromptCaptureSystem

app = FastAPI(title="Prompt Capture Webhook", version="1.0.0")

# Initialize the capture system
capture_system = PromptCaptureSystem()

class PromptRequest(BaseModel):
    """Request model for capturing a prompt."""
    prompt: str
    context: Optional[Dict[str, Any]] = None
    auto_commit: bool = True
    user: Optional[str] = None
    session_id: Optional[str] = None
    tags: Optional[list] = None

class PromptResponse(BaseModel):
    """Response model for captured prompt."""
    success: bool
    prompt_id: str
    topic: str
    word_count: int
    timestamp: str
    message: str

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Prompt Capture Webhook",
        "version": "1.0.0",
        "endpoints": {
            "/capture": "POST - Capture a new prompt",
            "/stats": "GET - Get capture statistics",
            "/prompts": "GET - List recent prompts",
            "/health": "GET - Health check"
        }
    }

@app.post("/capture", response_model=PromptResponse)
async def capture_prompt(request: PromptRequest, background_tasks: BackgroundTasks):
    """Capture a new prompt."""
    try:
        # Enhance context with request metadata
        context = request.context or {}
        context.update({
            "user": request.user or "anonymous",
            "session_id": request.session_id or "default",
            "tags": request.tags or [],
            "captured_via": "webhook",
            "timestamp": datetime.now().isoformat()
        })
        
        # Capture the prompt
        prompt_id = capture_system.save_prompt(request.prompt, context)
        topic = capture_system.extract_topic(request.prompt)
        
        # Git commit in background if requested
        if request.auto_commit:
            background_tasks.add_task(
                capture_system.git_commit_prompt,
                prompt_id,
                topic
            )
        
        return PromptResponse(
            success=True,
            prompt_id=prompt_id,
            topic=topic,
            word_count=len(request.prompt.split()),
            timestamp=datetime.now().isoformat(),
            message=f"Prompt captured successfully with ID: {prompt_id}"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_statistics():
    """Get prompt capture statistics."""
    try:
        stats = capture_system.get_statistics()
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prompts")
async def list_recent_prompts(limit: int = 10):
    """List recent captured prompts."""
    try:
        prompts = []
        metadata_dir = os.path.join(capture_system.prompts_dir, "metadata")
        
        if os.path.exists(metadata_dir):
            files = sorted(os.listdir(metadata_dir), reverse=True)[:limit]
            
            for filename in files:
                if filename.endswith('.json'):
                    import json
                    with open(os.path.join(metadata_dir, filename), 'r') as f:
                        data = json.load(f)
                        prompts.append({
                            "id": data.get("id"),
                            "timestamp": data.get("timestamp"),
                            "topic": data.get("topic"),
                            "word_count": data.get("word_count")
                        })
        
        return {
            "success": True,
            "prompts": prompts,
            "count": len(prompts),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Prompt Capture Webhook",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    # Run the webhook server
    uvicorn.run(app, host="0.0.0.0", port=8003)
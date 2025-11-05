"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables from .env file in backend directory
backend_dir = Path(__file__).parent.parent.parent
env_file = backend_dir / ".env"
load_dotenv(dotenv_path=env_file)

from .routes import rooms

app = FastAPI(
    title="Dispatcher Agents API",
    description="LiveKit Voice Agent Conversation System",
    version="2.0.0"
)

# Register routers
app.include_router(rooms.router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # Alternative frontend port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Dispatcher Agents API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


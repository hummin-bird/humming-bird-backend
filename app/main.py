from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import elevenlabs_webhook
from app.core.config import settings

app = FastAPI(
    title="Humming Bird Backend",
    description="Backend API for Humming Bird application",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(elevenlabs_webhook.router, prefix="/api/v1", tags=["webhooks"])

@app.get("/")
async def root():
    return {"message": "Welcome to Humming Bird Backend API"} 
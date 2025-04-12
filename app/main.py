from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.routes.route import router
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Humming Bird Backend",
    description="Backend API for Humming Bird application",
    version="0.1.0",
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
app.include_router(router, prefix="/api/v1")

# Add a middleware to handle WebSocket connections
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/ws/"):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

@app.get("/")
async def root():
    return {"message": "Welcome to Humming Bird Backend API"}

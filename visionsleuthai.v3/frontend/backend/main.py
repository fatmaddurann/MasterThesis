import os
import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routes import video_analysis, forensic_report, live_analysis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VisionSleuth AI API",
    description="Backend API for VisionSleuth AI",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "https://master-thesis-nu.vercel.app",
    "http://localhost:3000",
    "http://localhost:3001",
]

# Vercel preview pattern
vercel_preview_pattern = r"https://master-thesis-.*\.vercel\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow ALL origins
    allow_origin_regex=None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(video_analysis.router, prefix="/api/video", tags=["video"])
app.include_router(forensic_report.router, prefix="/api/forensic", tags=["forensic"])
app.include_router(live_analysis.router, prefix="/api/live", tags=["live"])

# Health check endpoint
@app.get("/")
async def root():
    return {"status": "online", "message": "VisionSleuth AI API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Debug endpoint
@app.get("/debug/routes")
async def list_routes(request: Request):
    url_list = [
        {"path": route.path, "name": route.name}
        for route in request.app.routes
    ]
    return {"routes": url_list}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

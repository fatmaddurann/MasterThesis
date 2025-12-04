import os
import logging
import uvicorn
from fastapi import FastAPI
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
    description="Backend API for VisionSleuth AI - Forensic Video Analysis",
    version="1.0.0"
)

# CORS Configuration
# Allow requests from frontend domains
origins = [
    "https://master-thesis-nu.vercel.app",  # Production Vercel frontend - EXACT MATCH REQUIRED
    "http://localhost:3000",  # Local development
    "http://localhost:3001",  # Alternative local port
]

# Vercel preview deployment pattern: https://master-thesis-*-*.vercel.app
# Using regex pattern to match all Vercel preview deployments
vercel_preview_pattern = r"https://master-thesis-.*\.vercel\.app"

logger.info(f"CORS middleware configured with allowed origins: {origins}")
logger.info(f"CORS middleware configured with Vercel preview pattern: {vercel_preview_pattern}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specific origins (exact match required when allow_credentials=True)
    allow_origin_regex=vercel_preview_pattern,  # Allow all Vercel preview deployments
    allow_credentials=True,  # Allow credentials (cookies, auth headers)
    allow_methods=["*"],  # Allow all methods (includes OPTIONS automatically)
    allow_headers=["*"],  # Allow all headers (simpler and more reliable)
    expose_headers=["*"],  # Expose all response headers to browser
    max_age=3600,  # Cache preflight responses for 1 hour
)
logger.info("CORS middleware added successfully")

# Include routers
app.include_router(video_analysis.router, prefix="/api/video", tags=["video"])
app.include_router(forensic_report.router, prefix="/api/forensic", tags=["forensic"])
app.include_router(live_analysis.router, prefix="/api/live", tags=["live"])

# Health check endpoint - CRITICAL for Render
@app.get("/")
async def root():
    return {"status": "online", "message": "VisionSleuth AI API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

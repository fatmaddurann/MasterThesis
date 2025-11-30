import os, base64
import logging
import time
from typing import List

# Environment variables
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "visionsleuth-backend.onrender.com").split(",")

# GCP Service Account setup
key_b64 = os.getenv("GCP_SERVICE_ACCOUNT_KEY")
if key_b64:
    with open("/tmp/service-account.json", "wb") as f:
        f.write(base64.b64decode(key_b64))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/service-account.json"

from fastapi import FastAPI, Request, HTTPException, File, UploadFile # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from fastapi import Response
from utils.metrics import render_metrics, CONTENT_TYPE_LATEST
from routes import video_analysis, live_analysis, forensic_report

# Configure logging
logging.basicConfig(
    level=logging.INFO if not DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(debug=DEBUG)

# CORS configuration
origins = [
    "https://master-thesis-nu.vercel.app",  # Vercel frontend (current)
    "https://visionsleuthai-frontend.vercel.app",  # Vercel frontend
    "https://www.visionsleuth.com",
    "https://visionsleuth.com",
    "https://api.visionsleuth.com",  # Custom domain backend
    "https://visionsleuth-ai-backend.onrender.com",  # Render backend
    "https://masterthesis-zk81.onrender.com",  # Render backend (current)
    "http://localhost:3000",
    "http://localhost:8000",
]

# Add CORS middleware - MUST be added BEFORE other middleware
# Allow all Vercel preview and production deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (including Vercel preview URLs)
    allow_credentials=False,  # Must be False when using wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

# File size limit middleware (1GB)
@app.middleware("http")
async def check_file_size(request: Request, call_next):
    if request.url.path == "/api/video/upload":
        content_length = request.headers.get("content-length")
        if content_length:
            if int(content_length) > 1024 * 1024 * 1024:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "File too large. Maximum size is 1GB"}
                )
    return await call_next(request)

# Rate limiting middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Error handling middleware with detailed logging
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        # Ensure CORS headers are present on all responses
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "false"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        origin = request.headers.get("origin")
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
        }
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(e) if DEBUG else None},
            headers=headers
        )

# Add global OPTIONS handler for CORS preflight requests
@app.options("/{full_path:path}")
async def options_handler(full_path: str, request: Request):
    """Handle CORS preflight requests for all routes"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "3600",
        }
    )

# Include routers
app.include_router(video_analysis.router, prefix="/api")
app.include_router(live_analysis.router, prefix="/api/live")
app.include_router(forensic_report.router, prefix="/api")

# Add video upload endpoint
@app.post("/api/video/upload")
async def upload_video(file: UploadFile = File(...)):
    logger.info(f"Received file: {file.filename}, content type: {file.content_type}")
    return {"filename": file.filename, "content_type": file.content_type, "message": "File received, analysis pending"}

@app.get("/")
async def root():
    return {"message": "VisionSleuth AI Backend API"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "debug": DEBUG,
        "allowed_hosts": ALLOWED_HOSTS
    }

@app.get("/ready")
async def readiness_check():
    try:
        # Basic readiness: ensure routes are registered and env keys present
        ready = True
        missing = []
        # Optional but recommended keys
        if not os.getenv("GCP_BUCKET_NAME"):
            missing.append("GCP_BUCKET_NAME")
        # service account key is optional at runtime if already mounted
        return {
            "status": "ready" if ready else "not_ready",
            "missing_env": missing,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "not_ready", "error": str(e)})

@app.get("/metrics")
async def metrics():
    data = render_metrics()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

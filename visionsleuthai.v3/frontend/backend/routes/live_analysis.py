from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from typing import Dict, List
import asyncio
import cv2
import numpy as np
from datetime import datetime
from models.crime_detection_model import CrimeDetectionModel
from models.video_processor import VideoProcessor
import base64
from fastapi.responses import JSONResponse, Response
import logging
import os
from utils.metrics import frames_processed, frames_dropped, start_timer, observe_latency_ms

router = APIRouter()
logger = logging.getLogger(__name__)
active_connections: Dict[str, WebSocket] = {}
video_processors: Dict[str, VideoProcessor] = {}
client_locks: Dict[str, asyncio.Lock] = {}
client_frame_counts: Dict[str, int] = {}
client_last_ts_ms: Dict[str, int] = {}

# Minimum interval between processed frames per client (ms)
MIN_INTERVAL_MS = int(os.getenv("LIVE_MIN_INTERVAL_MS", "120"))

# Allowed origins for CORS
ALLOWED_ORIGINS = [
    "https://master-thesis-nu.vercel.app",
    "http://localhost:3000",
    "http://localhost:3001",
]

def get_cors_headers(origin: str = None) -> dict:
    """Get CORS headers for response"""
    headers = {
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, Origin, X-Requested-With",
        "Access-Control-Max-Age": "3600",
    }
    if origin and origin in ALLOWED_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    elif not origin:
        # If no origin header, allow the production origin as fallback
        headers["Access-Control-Allow-Origin"] = "https://master-thesis-nu.vercel.app"
        headers["Access-Control-Allow-Credentials"] = "true"
    return headers

# Initialize model and processor once (lazy load inside model) - LIVE ANALYSIS MODE
model = CrimeDetectionModel(mode="live_analysis")
video_processor = VideoProcessor(model, mode="live_analysis")

@router.post("/start")
async def start_live_analysis():
    """Start live video analysis session"""
    return {"status": "success", "message": "Live analysis started"}

@router.websocket("/feed/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    
    # Initialize video processor for this connection - LIVE ANALYSIS MODE
    model = CrimeDetectionModel(mode="live_analysis")
    video_processor = VideoProcessor(model, mode="live_analysis")
    video_processors[client_id] = video_processor
    client_locks[client_id] = asyncio.Lock()
    client_frame_counts[client_id] = 0
    client_last_ts_ms[client_id] = 0
    
    try:
        while True:
            # Receive frame as bytes
            frame_data = await websocket.receive_bytes()
            
            # Convert bytes to numpy array
            frame_array = np.frombuffer(frame_data, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            # Rate limit and drop policy: try to acquire lock without waiting
            lock = client_locks[client_id]
            if lock.locked():
                frames_dropped.labels(client_id=client_id, reason="locked").inc()
                continue
            now_ms = int(datetime.utcnow().timestamp() * 1000)
            if now_ms - client_last_ts_ms.get(client_id, 0) < MIN_INTERVAL_MS:
                frames_dropped.labels(client_id=client_id, reason="rate_limited").inc()
                continue

            async with lock:
                try:
                    t0 = start_timer()
                    results = video_processor.process_frame(frame)
                except Exception as e:
                    logger.exception("Live WS frame processing error: %s", str(e))
                    await websocket.send_json({
                        "error": "processing_error",
                        "message": str(e)
                    })
                    continue
                elapsed_ms = observe_latency_ms(t0)
                client_frame_counts[client_id] += 1
                client_last_ts_ms[client_id] = now_ms
                frames_processed.labels(client_id=client_id).inc()
                logger.debug(f"client={client_id} frame={client_frame_counts[client_id]} latency_ms={elapsed_ms:.1f} det={len(results['detections'])}")
            
            # Send results back to client
            await websocket.send_json({
                "frame_number": client_frame_counts[client_id],
                "timestamp": datetime.utcnow().isoformat(),
                "detections": results["detections"],
                "suspicious_interactions": results["suspicious_interactions"]
            })
            
    except WebSocketDisconnect:
        # Cleanup on disconnect
        if client_id in active_connections:
            del active_connections[client_id]
        if client_id in video_processors:
            del video_processors[client_id]
        if client_id in client_locks:
            del client_locks[client_id]
        if client_id in client_frame_counts:
            del client_frame_counts[client_id]
        if client_id in client_last_ts_ms:
            del client_last_ts_ms[client_id]
    except Exception as e:
        logger.exception("WebSocket error: %s", str(e))
        if client_id in active_connections:
            await websocket.close(code=1001, reason=str(e))

@router.options("/frame")
async def options_frame(request: Request):
    """Handle CORS preflight requests for /frame endpoint"""
    origin = request.headers.get("origin")
    headers = get_cors_headers(origin)
    return Response(status_code=200, headers=headers)

@router.post("/frame")
async def live_analysis_frame(request: Request):
    try:
        # Parse request body
        data = await request.json()
        image_b64 = data.get("image")
        origin = request.headers.get("origin")
        cors_headers = get_cors_headers(origin)
        
        if not image_b64:
            return JSONResponse(
                status_code=400,
                content={"detections": [], "error": "No image data received"},
                headers=cors_headers
            )

        try:
            # Decode base64 image
            header, encoded = image_b64.split(",", 1) if "," in image_b64 else ("", image_b64)
            img_bytes = base64.b64decode(encoded)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return JSONResponse(
                    status_code=400,
                    content={"detections": [], "error": "Invalid image data"},
                    headers=cors_headers
                )

        except Exception as e:
            logger.warning("Image decode error: %s", str(e))
            return JSONResponse(
                status_code=400,
                content={"detections": [], "error": f"Image decode error: {str(e)}"},
                headers=cors_headers
            )

        # Process frame
        try:
            # Simple rate limit for REST path as well
            results = video_processor.process_frame(frame)
            return JSONResponse(
                content={
                    "detections": results["detections"],
                    "suspicious_interactions": results.get("suspicious_interactions", []),
                    "timestamp": datetime.utcnow().isoformat()
                },
                headers=cors_headers
            )
        except Exception as e:
            logger.exception("Model error: %s", str(e))
            return JSONResponse(
                status_code=500,
                content={"detections": [], "error": f"Model error: {str(e)}"},
                headers=cors_headers
            )

    except Exception as e:
        logger.exception("General error: %s", str(e))
        origin = request.headers.get("origin") if 'request' in locals() else None
        cors_headers = get_cors_headers(origin)
        return JSONResponse(
            status_code=500,
            content={"detections": [], "error": f"General error: {str(e)}"},
            headers=cors_headers
        ) 
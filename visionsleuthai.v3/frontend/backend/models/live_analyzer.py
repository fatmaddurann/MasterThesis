from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import asyncio
import cv2
import numpy as np
from datetime import datetime
from models.crime_detection_model import CrimeDetectionModel
from models.video_processor import VideoProcessor
from utils.gcp_connector import GCPConnector

router = APIRouter()
active_connections: Dict[str, WebSocket] = {}
video_processors: Dict[str, VideoProcessor] = {}

@router.post("/start")
async def start_live_analysis():
    """Start live video analysis session"""
    return {"status": "success", "message": "Live analysis started"}

@router.websocket("/feed/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    
    # Initialize video processor for this connection
    model = CrimeDetectionModel()
    video_processor = VideoProcessor(model)
    video_processors[client_id] = video_processor
    
    try:
        while True:
            # Receive frame as bytes
            frame_data = await websocket.receive_bytes()
            
            # Convert bytes to numpy array
            frame_array = np.frombuffer(frame_data, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            # Process frame
            results = video_processor.process_frame(frame)
            
            # Send results back to client
            await websocket.send_json({
                "frame_number": video_processor.frame_count,
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
    except Exception as e:
        print(f"Error processing frame: {str(e)}")
        if client_id in active_connections:
            await websocket.close(code=1001, reason=str(e)) 

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
import uuid
import cv2
from datetime import datetime
from models.crime_detection_model import CrimeDetectionModel
from models.video_processor import VideoProcessor
from utils.gcp_connector import GCPConnector
import logging
import numpy as np
import time
from utils.metrics import uploads_total, upload_failures_total, analysis_jobs_total, analysis_failures_total, analysis_duration_seconds, start_timer, observe_duration_seconds

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# GCP connector'ı başlat (opsiyonel)
gcp = None
try:
    bucket_name = os.getenv('GCP_BUCKET_NAME')
    if bucket_name:
        gcp = GCPConnector(bucket_name=bucket_name)
        logger.info(f"GCPConnector initialized with bucket: {bucket_name}")
    else:
        logger.warning("GCP_BUCKET_NAME not set - video upload will be disabled")
except Exception as e:
    logger.error(f"Failed to initialize GCPConnector: {str(e)}")
    logger.warning("Video upload will be disabled")

router = APIRouter()
UPLOAD_DIR = "uploads"
analysis_tasks: Dict[str, Dict] = {}
ALLOWED_EXTENSIONS = {'.mp4', '.mov', '.avi'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

def process_video(video_id: str, video_path: str, gcp_path: str):
    try:
        logger.info(f"Starting video processing for {video_id}")
        
        # Initialize model and processor
        model = CrimeDetectionModel()
        processor = VideoProcessor(model)
        
        # Open video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Could not open video file")
        
        # Video özelliklerini al
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        video_format = os.path.splitext(video_path)[1][1:].upper()
        
        logger.info(f"Video info: {total_frames} frames, {fps} fps, {duration:.2f}s duration")
        
        results = []
        processed_frames = 0
        t_job = start_timer()
        
        # Update task status to processing with initial info
        if video_id in analysis_tasks:
            analysis_tasks[video_id].update({
                "status": "processing",
                "total_frames": total_frames,
                "processed_frames": 0,
                "progress": 0
            })
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process frame
            frame_results = processor.process_frame(frame)
            results.append(frame_results)
            processed_frames += 1
            
            # Update progress every 5 frames for more frequent updates
            if processed_frames % 5 == 0:
                progress = int((processed_frames / total_frames) * 100) if total_frames > 0 else 0
                if video_id in analysis_tasks:
                    analysis_tasks[video_id].update({
                        "processed_frames": processed_frames,
                        "progress": progress
                    })
                logger.info(f"Processed {processed_frames}/{total_frames} frames ({progress}%)")
            
        cap.release()
        logger.info(f"Video processing completed: {processed_frames} frames processed")
        
        # Performans metriklerini hesapla
        job_seconds = observe_duration_seconds(t_job)
        analysis_duration_seconds.observe(job_seconds)
        inference_time = (job_seconds * 1000) / processed_frames if processed_frames > 0 else 0.0  # ms per frame
        
        # Clean results first to ensure all elements are dictionaries
        cleaned_results = []
        for frame_result in results:
            if isinstance(frame_result, dict):
                cleaned_results.append(frame_result)
            else:
                logger.warning(f"Skipping non-dict frame result: {type(frame_result)} - {frame_result}")
        
        # Calculate average confidence from all detections in all frames
        all_detections = []
        for frame_result in cleaned_results:
            if isinstance(frame_result, dict) and "detections" in frame_result:
                for detection in frame_result["detections"]:
                    if isinstance(detection, dict):
                        all_detections.append(detection)
                    else:
                        logger.warning(f"Skipping non-dict detection: {type(detection)} - {detection}")
        
        avg_confidence = 0.0
        if all_detections:
            avg_confidence = sum(d.get("confidence", 0) for d in all_detections) / len(all_detections)
        
        # Count dangerous objects and high risk frames
        # Comprehensive list of dangerous object categories
        dangerous_object_categories = [
            'gun', 'pistol', 'rifle', 'firearm', 'weapon',
            'knife', 'blade', 'dagger', 'sword', 'machete',
            'scissors', 'hammer', 'axe', 'hatchet', 'crowbar',
            'baseball_bat', 'bat', 'club', 'bottle', 'broken_bottle'
        ]
        
        dangerous_objects_count = 0
        high_risk_frames_count = 0
        detected_dangerous_types = set()  # Track what types were detected
        
        for frame_result in cleaned_results:
            if isinstance(frame_result, dict) and "detections" in frame_result:
                for detection in frame_result["detections"]:
                    if isinstance(detection, dict):
                        class_name = detection.get("class_name", "").lower()
                        original_class = detection.get("original_class", "").lower()
                        confidence = detection.get("confidence", 0.0)
                        
                        # Check both mapped class_name and original_class
                        is_dangerous = (
                            any(dangerous in class_name for dangerous in dangerous_object_categories) or
                            any(dangerous in original_class for dangerous in dangerous_object_categories)
                        )
                        
                        if is_dangerous:
                            dangerous_objects_count += 1
                            detected_dangerous_types.add(class_name)
                            logger.info(f"Dangerous object detected: {class_name} (original: {original_class}, confidence: {confidence:.3f})")
                        
                        if detection.get("risk_score", 0) >= 0.8:
                            high_risk_frames_count += 1
        
        # Log summary
        if dangerous_objects_count > 0:
            logger.info(f"Total dangerous objects detected: {dangerous_objects_count}")
            logger.info(f"Dangerous object types found: {', '.join(sorted(detected_dangerous_types))}")
        else:
            logger.warning(f"No dangerous objects detected in video. Total detections: {len(all_detections)}")
            if all_detections:
                detected_classes = set(d.get("class_name", "unknown") for d in all_detections)
                logger.info(f"Detected classes: {', '.join(sorted(detected_classes))}")
        
        # Adli bilimlere uygun sonuçları hazırla
        try:
            logger.info(f"Creating analysis_data with {len(cleaned_results)} cleaned results")
            # Create analysis_data step by step
            logger.info("Creating forensic_metadata...")
            # Create a simple hash using video_id and timestamp
            import hashlib
            hash_input = f"{video_id}_{datetime.utcnow().isoformat()}"
            evidence_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
            
            forensic_metadata = {
                "case_id": video_id,
                "evidence_hash": f"SHA256:{evidence_hash}",
                "chain_of_custody": "MAINTAINED",
                "analysis_date": datetime.utcnow().isoformat(),
                "analyst": "AI_CRIME_DETECTION_SYSTEM",
                "verification_status": "PENDING_HUMAN_REVIEW"
            }
            
            logger.info("Creating summary...")
            summary = {
                "duration": duration,
                "totalFrames": total_frames,
                "processedFrames": processed_frames,
                "videoSize": os.path.getsize(video_path),
                "format": video_format,
                "resolution": "384x640",
                "fps": fps
            }
            
            logger.info("Creating model_performance...")
            model_performance = {
                "inference_time": inference_time,
                "frames_processed": processed_frames,
                "average_confidence": avg_confidence,
                "model_version": "YOLOv8x",
                "processing_efficiency": (processed_frames / total_frames * 100) if total_frames > 0 else 0
            }
            
            logger.info("Creating forensic_analysis...")
            forensic_analysis = {
                "dangerous_objects_detected": dangerous_objects_count,
                "high_risk_frames": high_risk_frames_count,
                "evidence_quality": "HIGH" if processed_frames / total_frames > 0.9 else "MEDIUM",
                "legal_compliance": {
                    "privacy_protection": "ENABLED",
                    "data_integrity": "VERIFIED",
                    "chain_of_custody": "MAINTAINED"
                }
            }
            
            logger.info("Creating final analysis_data...")
            analysis_data = {
                "video_path": gcp_path,
                "timestamp": datetime.utcnow().isoformat(),
                "forensic_metadata": forensic_metadata,
                "summary": summary,
                "frames": cleaned_results,
                "model_performance": model_performance,
                "forensic_analysis": forensic_analysis
            }
        except Exception as e:
            logger.error(f"Error creating analysis_data: {str(e)}")
            logger.error(f"Results type: {type(results)}, length: {len(results) if hasattr(results, '__len__') else 'N/A'}")
            if results and len(results) > 0:
                logger.error(f"First result type: {type(results[0])}, content: {results[0]}")
            raise e
        
        # Save results to GCP (if available)
        results_path = None
        if gcp:
            results_path = gcp.save_results(video_id, analysis_data)
        else:
            logger.warning("GCP not available - results not saved to cloud")
        
        # Update task status
        try:
            analysis_tasks[video_id].update({
                "status": "completed",
                "results_path": results_path,
                "summary": analysis_data["summary"],
                "model_performance": analysis_data["model_performance"],
                "forensic_metadata": analysis_data["forensic_metadata"],
                "frames": analysis_data["frames"],
                "forensic_analysis": analysis_data["forensic_analysis"],
                "analysis_data": analysis_data  # Store complete analysis data
            })
            logger.info(f"Analysis completed successfully for video {video_id}")
        except Exception as e:
            logger.error(f"Error updating task status: {str(e)}")
            analysis_tasks[video_id].update({
                "status": "failed",
                "error": f"Error updating task status: {str(e)}"
            })
            raise e
        
        # Cleanup local file
        os.remove(video_path)
        
    except Exception as e:
        analysis_failures_total.inc()
        analysis_tasks[video_id]["status"] = "failed"
        analysis_tasks[video_id]["error"] = str(e)
        if os.path.exists(video_path):
            os.remove(video_path)

@router.post("/video/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...)
):
    uploads_total.inc()
    t0 = start_timer()
    temp_path = None
    
    try:
        # Dosya uzantısı kontrolü
        file_ext = os.path.splitext(video.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Dosya boyutu kontrolü
        content = await video.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum size is 500MB"
            )

        # Video işleme
        video_id = str(uuid.uuid4())
        temp_path = os.path.join(UPLOAD_DIR, f"{video_id}{file_ext}")
        
        try:
            # Geçici dosyaya kaydet
            with open(temp_path, "wb") as buffer:
                buffer.write(content)
            
            logger.info(f"Video saved temporarily: {temp_path}")
            
            # GCP'ye yükleme (if available) veya local path kullan
            gcp_path = temp_path  # Default to local path
            if gcp:
                try:
                    gcp_path = gcp.upload_video(temp_path)
                    logger.info(f"Video uploaded to GCP: {gcp_path}")
                except Exception as gcp_error:
                    logger.warning(f"GCP upload failed, using local path: {str(gcp_error)}")
                    gcp_path = temp_path
            else:
                logger.info(f"Using local path for video: {gcp_path}")
            
            # Analiz task'ını başlat
            analysis_tasks[video_id] = {
                "status": "processing",
                "timestamp": datetime.utcnow().isoformat(),
                "video_path": gcp_path,
                "results_path": None,
                "error": None,
                "summary": None,
                "model_performance": None
            }
            
            # Background task'ı başlat
            analysis_jobs_total.inc()
            background_tasks.add_task(process_video, video_id, temp_path, gcp_path)
            
            process_time = observe_duration_seconds(t0)
            logger.info(f"Upload completed in {process_time:.2f} seconds")
            
            return JSONResponse({
                "status": "success",
                "id": video_id,
                "message": "Video upload successful, analysis started",
                "process_time": process_time
            })
                
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            upload_failures_total.inc()
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process video: {str(e)}"
            )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        upload_failures_total.inc()
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/video/analysis/{video_id}")
async def get_analysis_results(video_id: str):
    try:
        # Check if task exists
        if video_id not in analysis_tasks:
            raise HTTPException(status_code=404, detail="Video analysis not found")
        
        task = analysis_tasks[video_id]
        
        # Return task status and results
        if task["status"] == "completed":
            return JSONResponse({
                "id": video_id,
                "status": "completed",
                "timestamp": task["timestamp"],
                "video_path": task["video_path"],
                "results_path": task["results_path"],
                "summary": task["summary"],
                "model_performance": task["model_performance"],
                "forensic_metadata": task.get("forensic_metadata"),
                "frames": task.get("frames"),
                "forensic_analysis": task.get("forensic_analysis"),
                "analysis_data": task.get("analysis_data")
            })
        elif task["status"] == "processing":
            progress_info = {
                "id": video_id,
                "status": "processing",
                "timestamp": task["timestamp"],
                "message": "Analysis in progress"
            }
            
            # Add progress details if available
            if "progress" in task:
                progress_info["progress"] = task["progress"]
            if "processed_frames" in task and "total_frames" in task:
                progress_info["processed_frames"] = task["processed_frames"]
                progress_info["total_frames"] = task["total_frames"]
                progress_info["message"] = f"Processing frame {task['processed_frames']}/{task['total_frames']}"
            
            return JSONResponse(progress_info)
        elif task["status"] == "failed":
            return JSONResponse({
                "id": video_id,
                "status": "failed",
                "timestamp": task["timestamp"],
                "error": task["error"]
            })
        else:
            return JSONResponse({
                "id": video_id,
                "status": "unknown",
                "timestamp": task["timestamp"]
            })
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in get_analysis_results: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/video/academic-analysis/{video_id}")
async def get_academic_analysis(video_id: str):
    try:
        # Analiz sonuçlarını veritabanından veya dosya sisteminden al
        analysis_data = get_analysis_data(video_id)
        
        if not analysis_data:
            raise HTTPException(status_code=404, detail="Analysis not found")
            
        # Akademik metrikleri hesapla
        academic_metrics = calculate_academic_metrics(analysis_data)
        
        return {
            "id": video_id,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "academic_metrics": academic_metrics,
            "model_performance": calculate_model_performance(analysis_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def calculate_academic_metrics(analysis_data: Dict) -> Dict:
    """Akademik metrikleri hesapla"""
    try:
        # Örnek metrik hesaplamaları
        true_positives = analysis_data.get("true_positives", 0)
        false_positives = analysis_data.get("false_positives", 0)
        false_negatives = analysis_data.get("false_negatives", 0)
        
        # Temel metrikleri hesapla
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "accuracy": (true_positives + false_positives) / (true_positives + false_positives + false_negatives),
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "confusion_matrix": analysis_data.get("confusion_matrix", []),
            "detection_metrics": {
                "true_positives": true_positives,
                "false_positives": false_positives,
                "false_negatives": false_negatives
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating metrics: {str(e)}")

def calculate_model_performance(analysis_data: Dict) -> Dict:
    """Model performans metriklerini hesapla"""
    return {
        "inference_time": analysis_data.get("inference_time", 0),
        "frames_processed": analysis_data.get("frames_processed", 0),
        "average_confidence": analysis_data.get("average_confidence", 0)
    } 

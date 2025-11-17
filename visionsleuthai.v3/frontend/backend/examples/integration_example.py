"""
Integration Example: Adding Forensic Report Generation to Existing Routes

This example shows how to integrate the ForensicReportGenerator into your
existing API routes WITHOUT modifying any detection logic.

Example: Adding a new endpoint to generate forensic reports from detection results.
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
from datetime import datetime
from models.forensic_report_generator import ForensicReportGenerator
import logging

logger = logging.getLogger(__name__)

# Example router - you can add this to your existing routes
router = APIRouter()
report_generator = ForensicReportGenerator()


@router.post("/generate-forensic-report")
async def generate_forensic_report(request: Request):
    """
    Generate a forensic report from detection results.
    
    This endpoint takes detection results (from your existing detection system)
    and generates a professional forensic report WITHOUT modifying any detection values.
    
    Expected input format:
    {
        "timestamp": "2024-01-01T12:00:00",
        "detections": [
            {
                "label": "knife",  # or "type" or "class_name"
                "confidence": 0.92,
                "bbox": [100, 150, 200, 250],
                "risk_level": "High",  # optional
                "risk_score": 0.85    # optional
            },
            ...
        ]
    }
    """
    try:
        data = await request.json()
        
        # Validate input
        if "detections" not in data:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing 'detections' field in request"}
            )
        
        # Ensure timestamp is present
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat()
        
        # Generate the forensic report
        # NOTE: This does NOT modify any detection values - only interprets them
        report = report_generator.generate_report(data)
        
        return JSONResponse(
            content={
                "status": "success",
                "report": report,
                "timestamp": data["timestamp"],
                "detection_count": len(data.get("detections", []))
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        )
        
    except Exception as e:
        logger.exception("Error generating forensic report: %s", str(e))
        return JSONResponse(
            status_code=500,
            content={"error": f"Error generating report: {str(e)}"}
        )


# Example: How to add report generation to existing live analysis endpoint
# (This is just an example - you would add this logic to your existing route)

async def example_add_to_live_analysis(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example function showing how to add forensic report generation
    to your existing live analysis results.
    
    This function takes the results from video_processor.process_frame()
    and adds a forensic report WITHOUT modifying the detection values.
    """
    # Your existing detection results (unchanged)
    detections = results.get("detections", [])
    timestamp = results.get("timestamp", datetime.utcnow().isoformat())
    
    # Prepare data for report generator
    detection_data = {
        "timestamp": timestamp,
        "detections": detections  # Use detections as-is, no modification
    }
    
    # Generate forensic report
    forensic_report = report_generator.generate_report(detection_data)
    
    # Return enhanced results (original detections + report)
    enhanced_results = {
        **results,  # Keep all original detection data
        "forensic_report": forensic_report  # Add the report
    }
    
    return enhanced_results


# Example: How to add report generation to video analysis results
# (This is just an example - you would add this logic to your existing route)

def example_add_to_video_analysis(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example function showing how to add forensic report generation
    to your existing video analysis results.
    
    This function processes all frames and generates a comprehensive report.
    """
    frames = analysis_data.get("frames", [])
    
    # Collect all detections from all frames
    all_detections = []
    for frame in frames:
        frame_detections = frame.get("detections", [])
        all_detections.extend(frame_detections)
    
    # Generate comprehensive forensic report
    detection_data = {
        "timestamp": analysis_data.get("timestamp", datetime.utcnow().isoformat()),
        "detections": all_detections
    }
    
    forensic_report = report_generator.generate_report(detection_data)
    
    # Add report to analysis data (without modifying detection values)
    analysis_data["forensic_report"] = forensic_report
    
    return analysis_data


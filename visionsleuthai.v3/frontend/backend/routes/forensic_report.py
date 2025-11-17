"""
Forensic Report API Routes

This module provides API endpoints for generating professional forensic reports
from detection results using the ForensicReportGenerator.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List, Any
from datetime import datetime
from models.forensic_report_generator import ForensicReportGenerator
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
report_generator = ForensicReportGenerator()


@router.post("/forensic/generate-report")
async def generate_forensic_report(request: Request):
    """
    Generate a professional forensic report from detection results.
    
    This endpoint takes detection results and generates a comprehensive
    forensic report WITHOUT modifying any detection values.
    
    Expected input format:
    {
        "timestamp": "ISO format timestamp (optional)",
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
    
    Returns:
    {
        "status": "success",
        "report": "Full forensic report text",
        "timestamp": "Report generation timestamp",
        "detection_count": 5
    }
    """
    try:
        data = await request.json()
        
        # Validate input
        if "detections" not in data:
            raise HTTPException(
                status_code=400,
                detail="Missing 'detections' field in request"
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
                "detection_count": len(data.get("detections", [])),
                "report_length": len(report)
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error generating forensic report: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error generating report: {str(e)}"
        )


import torch
import os
import logging
from typing import Dict, Any, Tuple, List
import numpy as np
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class CrimeDetectionModel:
    def __init__(self, mode: str = "video_upload"):
        """
        Initialize CrimeDetectionModel with mode parameter.
        
        Args:
            mode: "video_upload" (default, no changes) or "live_analysis" (all improvements active)
        """
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.mode = mode
        
        # MOD AYIRIMI: Live analysis için tüm sınırları kaldır
        if mode == "live_analysis":
            # Live mod: Çok düşük threshold, tüm nesneler ve insanlar algılanacak - MESAFE SINIRI YOK
            base_threshold = 0.25  # Daha düşük threshold ile tüm nesneler algılanır
            logger.info(f"LIVE ANALYSIS MODE: Confidence threshold set to {base_threshold}, no size/distance limits - ALL objects and people will be detected")
        else:
            # Video upload mod: Lower threshold for better weapon detection
            # Standard YOLOv8 doesn't detect weapons well, so we lower threshold
            base_threshold = float(os.getenv("MODEL_CONFIDENCE_THRESHOLD", "0.35"))
            logger.info(f"VIDEO UPLOAD MODE: Confidence threshold set to {base_threshold} for better dangerous object detection")
        
        # Base threshold
        self.confidence_threshold = base_threshold
        # Class-based thresholds (JSON mapping of class_name->threshold)
        self.class_thresholds: Dict[str, float] = {}
        try:
            import json
            ct = os.getenv("CLASS_THRESHOLDS", "")
            if ct:
                self.class_thresholds = json.loads(ct)
        except Exception:
            self.class_thresholds = {}
        # Simple temperature scaling (confidence calibration)
        try:
            self.temp_scale = float(os.getenv("CONFIDENCE_TEMP_SCALE", "1.0"))
        except Exception:
            self.temp_scale = 1.0
        # Model path/name - use YOLOv8x for better detection
        self.model_path = os.getenv("MODEL_PATH", "yolov8x.pt")
        
        # Dangerous object mapping for better crime detection
        # Expanded to include more variations and YOLOv8 class names
        self.dangerous_objects = {
            'knife': ['knife', 'blade', 'dagger', 'sword', 'cutting', 'sharp'],
            'gun': ['gun', 'pistol', 'rifle', 'firearm', 'weapon', 'handgun', 'revolver', 'shotgun', 'rifle', 'machine gun', 'submachine'],
            'weapon': ['weapon', 'gun', 'knife', 'pistol', 'rifle', 'firearm', 'blade', 'dagger', 'sword', 'handgun', 'revolver'],
            'scissors': ['scissors', 'shears', 'scissor'],
            'bottle': ['bottle', 'glass_bottle', 'broken_bottle', 'wine bottle', 'beer bottle'],
            'hammer': ['hammer', 'mallet', 'sledgehammer'],
            'crowbar': ['crowbar', 'pry_bar', 'prybar', 'wrecking bar'],
            'baseball_bat': ['baseball_bat', 'bat', 'club', 'baseball bat', 'cricket bat'],
            'axe': ['axe', 'hatchet', 'tomahawk'],
            'machete': ['machete', 'cleaver', 'chopper']
        }
        
        # YOLOv8 COCO class names that might indicate weapons (even if not perfect)
        # Note: Standard YOLOv8 doesn't have weapon classes, but we check for similar objects
        self.weapon_like_objects = [
            'remote', 'cell phone', 'hair drier', 'toothbrush',  # Objects that might be mistaken
            'handbag', 'backpack', 'suitcase',  # Containers that might hold weapons
        ]
        # NMS / inference options
        try:
            self.iou_threshold = float(os.getenv("NMS_IOU_THRESHOLD", "0.45"))
        except Exception:
            self.iou_threshold = 0.45
        self.agnostic_nms = os.getenv("NMS_CLASS_AGNOSTIC", "false").lower() == "true"

    def load_model(self) -> Dict[str, Any]:
        """Load the YOLOv8 model from local path or model hub name"""
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"Model loaded: {self.model_path} on {self.device}")
            return {
                "status": "loaded",
                "model_path": self.model_path,
                "device": str(self.device),
                "confidence_threshold": self.confidence_threshold
            }
        except Exception as e:
            logger.error(f"Failed to load model '{self.model_path}': {str(e)}")
            return {"status": "error", "message": str(e)}

    def _calibrate_conf(self, conf: float) -> float:
        # Simple temperature scaling: conf' = sigmoid(logit(conf)/T)
        # For stability fallback to linear scaling if conf is edge
        try:
            conf = float(conf)
            if conf <= 0.0:
                return 0.0
            if conf >= 1.0:
                return 1.0
            import math
            logit = math.log(conf / (1.0 - conf))
            scaled = 1.0 / (1.0 + math.exp(-logit / max(1e-6, self.temp_scale)))
            return float(max(0.0, min(1.0, scaled)))
        except Exception:
            # Fallback: linear scaling
            return float(max(0.0, min(1.0, conf / max(1e-6, self.temp_scale))))

    def process_frame(self, frame: np.ndarray) -> Tuple[List[Dict[str, Any]], np.ndarray]:
        """Process a single frame and return detections with annotated frame"""
        try:
            if self.model is None:
                load_status = self.load_model()
                if load_status.get("status") != "loaded":
                    raise ValueError(load_status.get("message", "Model not loaded"))

            # Run inference
            # Pass NMS/inference options
            results = self.model(
                frame,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                agnostic_nms=self.agnostic_nms
            )[0]

            detections: List[Dict[str, Any]] = []
            frame_height, frame_width = frame.shape[:2]
            
            for r in results.boxes.data.tolist():
                x1, y1, x2, y2, conf, cls = r
                cls_idx = int(cls)
                class_name = results.names[cls_idx]
                
                # LIVE MOD: Tüm nesneler algılanacak - boyut/mesafe sınırı YOK
                if self.mode == "live_analysis":
                    # Tüm detections kabul et - sınır yok
                    pass
                else:
                    # VIDEO UPLOAD MOD: Orjinal filtreleme (DEĞİŞMEZ)
                    # Boyut kontrolü (opsiyonel, orjinal kodda yoksa hiçbir şey yapma)
                    pass
                
                # Map to dangerous object categories
                mapped_class = self._map_to_dangerous_object(class_name)
                
                # LIVE MOD: Per-class threshold kullanma, sadece base threshold
                if self.mode == "live_analysis":
                    thr = self.confidence_threshold
                else:
                    # VIDEO UPLOAD MOD: Lower threshold for dangerous objects
                    # Use even lower threshold for potentially dangerous objects
                    if mapped_class in ['gun', 'weapon', 'knife', 'pistol', 'rifle', 'firearm']:
                        # Very low threshold for weapons (0.25) since YOLOv8 doesn't detect them well
                        thr = float(self.class_thresholds.get(mapped_class, 0.25))
                        logger.debug(f"Using lower threshold {thr} for dangerous object: {mapped_class}")
                    else:
                        thr = float(self.class_thresholds.get(mapped_class, self.confidence_threshold))
                
                calibrated = self._calibrate_conf(float(conf))
                
                # For video upload mode, also check original class name for weapon keywords
                # This helps catch objects that might be weapons but not properly classified
                if self.mode == "video_upload" and calibrated < thr:
                    # Check if original class name contains weapon keywords
                    class_lower = class_name.lower()
                    weapon_keywords = ['gun', 'pistol', 'rifle', 'firearm', 'weapon', 'knife', 'blade']
                    if any(keyword in class_lower for keyword in weapon_keywords):
                        # Use even lower threshold for potential weapons
                        thr = 0.20
                        logger.debug(f"Potential weapon detected in {class_name}, using threshold {thr}")
                
                if calibrated < thr:
                    continue
                    
                # Calculate risk level
                risk_level = self._calculate_risk_level(mapped_class, calibrated)
                
                detections.append({
                    "class_name": mapped_class,
                    "original_class": class_name,
                    "confidence": calibrated,
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "risk_level": risk_level
                })

            # LIVE MOD: Tüm nesneler için bounding box çiz (results.plot() kullan)
            annotated_frame = results.plot()
            return detections, annotated_frame
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            return [], frame

    def _map_to_dangerous_object(self, class_name: str) -> str:
        """Map detected class to dangerous object category"""
        class_name_lower = class_name.lower()
        
        # First check exact dangerous object matches
        for dangerous_type, variations in self.dangerous_objects.items():
            for variation in variations:
                if variation in class_name_lower:
                    logger.debug(f"Mapped {class_name} to dangerous object: {dangerous_type}")
                    return dangerous_type
        
        # Check for weapon-like patterns in class name
        weapon_keywords = ['gun', 'pistol', 'rifle', 'firearm', 'weapon', 'knife', 'blade', 'sword']
        for keyword in weapon_keywords:
            if keyword in class_name_lower:
                logger.debug(f"Found weapon keyword '{keyword}' in {class_name}, mapping to weapon")
                return 'weapon'
                    
        # If not a dangerous object, return original class
        return class_name
    
    def _calculate_risk_level(self, class_name: str, confidence: float) -> str:
        """Calculate risk level based on object type and confidence"""
        high_risk_objects = ['gun', 'knife', 'weapon', 'pistol', 'rifle', 'firearm', 'machete', 'axe']
        medium_risk_objects = ['scissors', 'hammer', 'crowbar', 'baseball_bat', 'bottle']
        
        if class_name in high_risk_objects:
            if confidence > 0.7:
                return "High"
            elif confidence > 0.5:
                return "Medium"
            else:
                return "Low"
        elif class_name in medium_risk_objects:
            if confidence > 0.8:
                return "Medium"
            else:
                return "Low"
        else:
            return "Low"
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "status": "loaded" if self.model is not None else "not_loaded",
            "device": str(self.device),
            "confidence_threshold": self.confidence_threshold,
            "model_type": "YOLOv8x",
            "dangerous_objects": list(self.dangerous_objects.keys())
        }

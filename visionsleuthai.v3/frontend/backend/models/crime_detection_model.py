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
        # Model path/name
        self.model_path = os.getenv("MODEL_PATH", "yolo11n.pt")
        
        # Versiyon Tespiti
        path_lower = self.model_path.lower()
        self.is_legacy_model = "yolov3" in path_lower
        self.is_yolo11 = "yolo11" in path_lower
        
        if self.is_yolo11:
            logger.info(f"LATEST MODE: Loading {self.model_path} (YOLO11 Architecture)")
            # YOLO11 daha hassas olduğu için threshold'u biraz daha yukarıda tutabiliriz
            self.confidence_threshold = float(os.getenv("MODEL_CONFIDENCE_THRESHOLD", "0.28"))
        elif self.is_legacy_model:
            logger.info(f"LEGACY MODE: Loading {self.model_path} (Darknet weights compatible)")
            self.confidence_threshold = 0.20
        else:
            logger.info(f"MODERN MODE: Loading {self.model_path} (YOLOv8 architecture)")
            self.confidence_threshold = base_threshold
        
        # Dangerous object mapping for better crime detection
        # Expanded to include more variations and YOLOv8 class names
        self.dangerous_objects = {
            'knife': ['knife', 'blade', 'dagger', 'sword', 'cutting', 'sharp', 'razor'],
            'gun': ['gun', 'pistol', 'rifle', 'firearm', 'weapon', 'handgun', 'revolver', 'shotgun', 'rifle', 'machine gun', 'submachine', 'glock', 'beretta'],
            'weapon': ['weapon', 'gun', 'knife', 'pistol', 'rifle', 'firearm', 'blade', 'dagger', 'sword', 'handgun', 'revolver', 'stick', 'pipe'],
            'scissors': ['scissors', 'shears', 'scissor'],
            'bottle': ['bottle', 'glass_bottle', 'broken_bottle', 'wine bottle', 'beer bottle'],
            'hammer': ['hammer', 'mallet', 'sledgehammer', 'tool'],
            'crowbar': ['crowbar', 'pry_bar', 'prybar', 'wrecking bar'],
            'baseball_bat': ['baseball_bat', 'bat', 'club', 'baseball bat', 'cricket bat'],
            'axe': ['axe', 'hatchet', 'tomahawk'],
            'machete': ['machete', 'cleaver', 'chopper']
        }
        
        # YOLOv8 COCO class names that might indicate weapons (even if not perfect)
        # Note: Standard YOLOv8 doesn't have weapon classes, but we check for similar objects
        self.weapon_like_objects = [
            'remote', 'cell phone', 'hair drier', 'toothbrush', 'umbrella', 'wine glass', 'cup'
        ]
        # NMS / inference options
        try:
            self.iou_threshold = float(os.getenv("NMS_IOU_THRESHOLD", "0.40")) # Slightly lower for overlapping objects
        except Exception:
            self.iou_threshold = 0.40
        self.agnostic_nms = os.getenv("NMS_CLASS_AGNOSTIC", "false").lower() == "true"

    def load_model(self) -> Dict[str, Any]:
        """Load the YOLOv8 model from local path, model hub name, or GCP bucket with optimizations"""
        try:
            # Handle GCP path if provided (Format: gcp://bucket-name/path/to/model.pt)
            if self.model_path.startswith("gcp://"):
                try:
                    import re
                    from utils.gcp_connector import GCPConnector
                    
                    # Parse gcp://bucket/blob
                    match = re.match(r"gcp://([^/]+)/(.+)", self.model_path)
                    if not match:
                        raise ValueError(f"Invalid GCP path format: {self.model_path}")
                    
                    bucket_name, blob_path = match.groups()
                    local_model_dir = os.path.join(os.path.dirname(__file__), 'temp_models')
                    os.makedirs(local_model_dir, exist_ok=True)
                    local_model_path = os.path.join(local_model_dir, os.path.basename(blob_path))
                    
                    # Download only if it doesn't exist
                    if not os.path.exists(local_model_path):
                        logger.info(f"Downloading model from GCP: {self.model_path} -> {local_model_path}")
                        gcp = GCPConnector(bucket_name=bucket_name)
                        gcp.download_file(blob_path, local_model_path)
                    
                    # Update model_path to local for YOLO loading
                    self.model_path = local_model_path
                except Exception as gcp_err:
                    logger.error(f"GCP model download failed: {str(gcp_err)}. Falling back to default.")
                    self.model_path = "yolov8n.pt"

            self.model = YOLO(self.model_path)
            
            # Optimize model for inference speed
            if self.device.type == 'cuda' and torch.cuda.is_available():
                # Move model to GPU and enable optimizations
                self.model.to(self.device)
                # Enable TensorRT if available (further speedup)
                try:
                    # This will be used automatically if TensorRT is available
                    pass
                except:
                    pass
            
            # Warm up model with dummy inference (reduces first inference latency)
            if self.mode == "live_analysis":
                try:
                    dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
                    _ = self.model(dummy_frame, verbose=False, conf=0.25)
                    logger.debug("Model warmup completed")
                except:
                    pass
            
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

            # Preprocessing optimization: resize if frame is too large (faster inference)
            original_shape = frame.shape
            max_size = 1280  # Max dimension for faster inference
            if max(original_shape[:2]) > max_size:
                scale = max_size / max(original_shape[:2])
                new_width = int(original_shape[1] * scale)
                new_height = int(original_shape[0] * scale)
                import cv2
                frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
                logger.debug(f"Resized frame from {original_shape} to {frame.shape} for faster inference")

            # Run inference with ByteTrack (SOTA tracking)
            # persist=True ensures tracks are maintained across process_frame calls
            results = self.model.track(
                frame,
                persist=True,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                agnostic_nms=True,
                half=use_half,
                verbose=False,
                max_det=50,
                imgsz=640,
                tracker="bytetrack.yaml" # or "botsort.yaml"
            )[0]

            detections: List[Dict[str, Any]] = []
            
            # Results now contain tracking IDs
            if results.boxes.id is not None:
                boxes = results.boxes.xyxy.cpu().numpy()
                confs = results.boxes.conf.cpu().numpy()
                clss = results.boxes.cls.cpu().numpy()
                ids = results.boxes.id.cpu().numpy()
                
                for box, conf, cls, track_id in zip(boxes, confs, clss, ids):
                    x1, y1, x2, y2 = box
                    cls_idx = int(cls)
                    class_name = results.names[cls_idx]
                    
                    mapped_class = self._map_to_dangerous_object(class_name, float(conf), [float(x1), float(y1), float(x2), float(y2)])
                    
                    # Version-based threshold logic
                    if self.is_yolo11:
                        thr = self.confidence_threshold
                    else:
                        thr = float(self.class_thresholds.get(mapped_class, self.confidence_threshold))
                    
                    calibrated = self._calibrate_conf(float(conf))
                    
                    if calibrated < thr:
                        continue
                        
                    risk_level = self._calculate_risk_level(mapped_class, calibrated)
                    
                    detections.append({
                        "class_name": mapped_class,
                        "original_class": class_name,
                        "confidence": calibrated,
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        "risk_level": risk_level,
                        "track_id": int(track_id) # Built-in Track ID
                    })
            else:
                # Fallback for frames with no tracks/detections
                for r in results.boxes.data.tolist():
                    # r might be [x1, y1, x2, y2, conf, cls] or [x1, y1, x2, y2, id, conf, cls]
                    if len(r) == 7:
                        x1, y1, x2, y2, track_id, conf, cls = r
                    else:
                        x1, y1, x2, y2, conf, cls = r
                        track_id = -1
                    
                    cls_idx = int(cls)
                    class_name = results.names[cls_idx]
                    mapped_class = self._map_to_dangerous_object(class_name, float(conf), [float(x1), float(y1), float(x2), float(y2)])
                    
                    calibrated = self._calibrate_conf(float(conf))
                    if calibrated < self.confidence_threshold: continue
                    
                    detections.append({
                        "class_name": mapped_class,
                        "original_class": class_name,
                        "confidence": calibrated,
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        "risk_level": self._calculate_risk_level(mapped_class, calibrated),
                        "track_id": int(track_id)
                    })

            # LIVE MOD: Tüm nesneler için bounding box çiz (results.plot() kullan)
            annotated_frame = results.plot()
            return detections, annotated_frame
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            return [], frame

    def _map_to_dangerous_object(self, class_name: str, confidence: float = 0.0, bbox: List[float] = None) -> str:
        """
        Map detected class to dangerous object category with false positive filtering.
        
        Args:
            class_name: Detected class name
            confidence: Detection confidence
            bbox: Bounding box [x1, y1, x2, y2] for aspect ratio analysis
        """
        class_name_lower = class_name.lower()
        
        # FALSE POSITIVE FILTERING: Common misclassifications for knives
        # These objects are often confused with knives but should NOT be mapped to knife
        # Context-aware filtering based on confidence, aspect ratio, and size
        knife_false_positives = {
            'toothbrush': {
                'min_confidence': 0.55,  # High confidence toothbrush = not a knife
                'aspect_ratio_range': (0.25, 0.75),  # Toothbrushes are longer/thinner
                'max_area_ratio': 0.02  # Toothbrushes are typically smaller relative to frame
            },
            'scissors': {
                'min_confidence': 0.45,  # Scissors have distinct shape (two blades)
                'aspect_ratio_range': (0.35, 0.85),  # Scissors are more square-ish
                'max_area_ratio': 0.03
            },
            'baseball_bat': {
                'min_confidence': 0.35,  # Baseball bats are much longer and thicker
                'aspect_ratio_range': (0.08, 0.35),  # Very long/thin
                'min_area_ratio': 0.01  # Baseball bats are typically larger
            },
            'remote': {
                'min_confidence': 0.5,
                'aspect_ratio_range': (0.4, 1.6),  # More square/rectangular
                'max_area_ratio': 0.015
            },
            'cell phone': {
                'min_confidence': 0.5,
                'aspect_ratio_range': (0.5, 2.0),  # Rectangular, can be portrait/landscape
                'max_area_ratio': 0.02
            },
            'hair drier': {
                'min_confidence': 0.5,
                'aspect_ratio_range': (0.3, 0.8),  # Similar to toothbrush
                'max_area_ratio': 0.02
            }
        }
        
        # Check if this is a known false positive for knife
        if class_name_lower in knife_false_positives:
            fp_config = knife_false_positives[class_name_lower]
            
            # If confidence is high enough, trust the original classification
            if confidence >= fp_config['min_confidence']:
                # Context-aware filtering: check aspect ratio and size
                if bbox is not None and len(bbox) >= 4:
                    width = bbox[2] - bbox[0]
                    height = bbox[3] - bbox[1]
                    if width > 0 and height > 0:
                        aspect_ratio = height / width
                        min_ar, max_ar = fp_config['aspect_ratio_range']
                        
                        # Calculate area ratio (for size-based filtering)
                        # Assuming frame dimensions are available (we'll use a default if not)
                        frame_area = 640 * 640  # Default frame size
                        bbox_area = width * height
                        area_ratio = bbox_area / frame_area if frame_area > 0 else 0
                        
                        # Check aspect ratio
                        ar_match = min_ar <= aspect_ratio <= max_ar
                        
                        # Check area ratio (if specified)
                        area_match = True
                        if 'max_area_ratio' in fp_config:
                            area_match = area_match and (area_ratio <= fp_config['max_area_ratio'])
                        if 'min_area_ratio' in fp_config:
                            area_match = area_match and (area_ratio >= fp_config['min_area_ratio'])
                        
                        # If both aspect ratio and area match false positive characteristics
                        if ar_match and area_match:
                            logger.debug(f"Filtered {class_name} (conf={confidence:.2f}, ar={aspect_ratio:.2f}, area_ratio={area_ratio:.4f}) - likely false positive for knife")
                            return class_name_lower  # Return original class, not knife
                
                # High confidence in false positive class = not a knife
                logger.debug(f"High confidence {class_name} (conf={confidence:.2f}) - not mapping to knife")
                return class_name_lower
        
        # First check exact dangerous object matches
        for dangerous_type, variations in self.dangerous_objects.items():
            for variation in variations:
                if variation in class_name_lower:
                    # Special handling: if it's a known false positive with high confidence, don't map
                    if class_name_lower in knife_false_positives and dangerous_type == 'knife':
                        if confidence >= knife_false_positives[class_name_lower]['min_confidence']:
                            logger.debug(f"Skipping knife mapping for high-confidence {class_name}")
                            continue
                    logger.debug(f"Mapped {class_name} to dangerous object: {dangerous_type}")
                    return dangerous_type
        
        # Check for weapon-like patterns in class name
        weapon_keywords = ['gun', 'pistol', 'rifle', 'firearm', 'weapon', 'knife', 'blade', 'sword']
        for keyword in weapon_keywords:
            if keyword in class_name_lower:
                # Skip if it's a known false positive
                if class_name_lower in knife_false_positives and keyword == 'knife':
                    if confidence >= knife_false_positives[class_name_lower]['min_confidence']:
                        continue
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
        model_ver = "YOLOv8x"
        if self.is_yolo11: model_ver = "YOLO11 (Latest)"
        elif self.is_legacy_model: model_ver = "YOLOv3 (Legacy)"
        
        return {
            "status": "loaded" if self.model is not None else "not_loaded",
            "device": str(self.device),
            "confidence_threshold": self.confidence_threshold,
            "model_type": model_ver,
            "dangerous_objects": list(self.dangerous_objects.keys())
        }

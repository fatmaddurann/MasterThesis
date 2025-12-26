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
            # Video upload mod: Very low threshold for better weapon detection
            # Standard YOLOv8 doesn't detect weapons well, so we use very low threshold
            # We'll filter later based on mapping and class-specific thresholds
            base_threshold = float(os.getenv("MODEL_CONFIDENCE_THRESHOLD", "0.20"))
            logger.info(f"VIDEO UPLOAD MODE: Confidence threshold set to {base_threshold} for aggressive dangerous object detection")
        
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
        # Model path/name - use YOLOv8n for faster inference on CPU (Render free tier)
        # Support GCP model path: if MODEL_PATH starts with "gcp://", download from GCP
        model_path_env = os.getenv("MODEL_PATH", "yolov8n.pt")
        
        # Check if model path is GCP path (format: gcp://bucket/path/to/model.pt or gcp://path/to/model.pt)
        if model_path_env.startswith("gcp://"):
            # Extract GCP path (remove gcp:// prefix)
            gcp_path_without_prefix = model_path_env[6:]  # Remove "gcp://"
            
            # Parse bucket name and model path
            # Format 1: gcp://bucket-name/path/to/model.pt
            # Format 2: gcp://path/to/model.pt (uses GCP_BUCKET_NAME env var)
            parts = gcp_path_without_prefix.split('/', 1)
            if len(parts) == 2:
                # Format 1: bucket name in path
                bucket_name_from_path = parts[0]
                gcp_model_path = parts[1]
            else:
                # Format 2: use GCP_BUCKET_NAME env var
                bucket_name_from_path = None
                gcp_model_path = gcp_path_without_prefix
            
            # Try to download from GCP
            try:
                from utils.gcp_connector import GCPConnector
                bucket_name = bucket_name_from_path or os.getenv("GCP_BUCKET_NAME")
                if bucket_name:
                    gcp = GCPConnector(bucket_name=bucket_name)
                    # Use local cache path: models/cached/{model_filename}
                    model_filename = os.path.basename(gcp_model_path)
                    local_cache_path = os.path.join(os.path.dirname(__file__), "cached", model_filename)
                    
                    # Download if not cached or cache is older than 1 day
                    should_download = True
                    if os.path.exists(local_cache_path):
                        import time
                        cache_age = time.time() - os.path.getmtime(local_cache_path)
                        if cache_age < 86400:  # 1 day
                            should_download = False
                            logger.info(f"Using cached model from {local_cache_path}")
                    
                    if should_download:
                        os.makedirs(os.path.dirname(local_cache_path), exist_ok=True)
                        if gcp.download_model(gcp_model_path, local_cache_path):
                            self.model_path = local_cache_path
                            logger.info(f"Model downloaded from GCP: {gcp_model_path} -> {local_cache_path}")
                        else:
                            # Fallback to default
                            logger.warning(f"Model not found at GCP path: {bucket_name}/{gcp_model_path}, using default: yolov8n.pt")
                            self.model_path = "yolov8n.pt"
                    else:
                        self.model_path = local_cache_path
                else:
                    logger.warning("GCP_BUCKET_NAME not set, cannot download model from GCP. Using default: yolov8n.pt")
                    self.model_path = "yolov8n.pt"
            except Exception as e:
                logger.warning(f"Failed to download model from GCP: {str(e)}. Using default: yolov8n.pt")
                self.model_path = "yolov8n.pt"
        else:
            # Regular local path or model hub name
            self.model_path = model_path_env
        
        # Dangerous object mapping for better crime detection
        # Updated to match GCP dataset structure (knife, handgun)
        # Expanded to include more variations and YOLOv8 class names
        self.dangerous_objects = {
            'knife': ['knife', 'blade', 'dagger', 'sword', 'cutting', 'sharp'],
            'handgun': ['handgun', 'gun', 'pistol', 'firearm', 'weapon', 'revolver'],  # Updated from 'gun'
            'gun': ['gun', 'pistol', 'rifle', 'firearm', 'weapon', 'handgun', 'revolver', 'shotgun', 'rifle', 'machine gun', 'submachine'],  # Keep for backward compatibility
            'weapon': ['weapon', 'gun', 'knife', 'pistol', 'rifle', 'firearm', 'blade', 'dagger', 'sword', 'handgun', 'revolver'],
            'scissors': ['scissors', 'shears', 'scissor'],
            'bottle': ['bottle', 'glass_bottle', 'broken_bottle', 'wine bottle', 'beer bottle'],
            'hammer': ['hammer', 'mallet', 'sledgehammer'],
            'crowbar': ['crowbar', 'pry_bar', 'prybar', 'wrecking bar'],
            'baseball_bat': ['baseball_bat', 'bat', 'club', 'baseball bat', 'cricket bat'],
            'axe': ['axe', 'hatchet', 'tomahawk'],
            'machete': ['machete', 'cleaver', 'chopper']
        }
        
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
        """Load the YOLOv8 model from local path or model hub name with optimizations"""
        try:
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

            # Run inference with optimizations for speed
            # Use half precision (FP16) if available for faster inference
            use_half = self.device.type == 'cuda' and torch.cuda.is_available()
            
            # CRITICAL: Use very low confidence threshold for video upload mode to catch weapons
            # YOLOv8 default model doesn't have handgun class, so we need to catch all potential objects
            # and then map them to dangerous categories
            inference_conf = self.confidence_threshold
            if self.mode == "video_upload":
                # Use very low threshold (0.15) to catch all potential weapons
                # We'll filter later based on mapping and class-specific thresholds
                inference_conf = 0.15
                logger.debug(f"Video upload mode: Using low inference threshold {inference_conf} to catch all potential weapons")
            
            # Optimize inference settings for dangerous object detection
            # Focus on speed while maintaining accuracy for weapons
            results = self.model(
                frame,
                conf=inference_conf,  # Use low threshold to catch all potential weapons
                iou=self.iou_threshold,
                agnostic_nms=self.agnostic_nms,
                half=use_half,  # Use FP16 on GPU for 2x speedup
                verbose=False,  # Disable verbose output for speed
                max_det=300,    # Increase max detections to catch more potential weapons
                imgsz=640,      # Fixed input size for consistent speed
            )[0]

            detections: List[Dict[str, Any]] = []
            frame_height, frame_width = frame.shape[:2]
            
            # Log all detected classes for debugging (first frame only)
            if not hasattr(self, '_logged_classes'):
                detected_classes = set(results.names[int(cls)] for _, _, _, _, _, cls in results.boxes.data.tolist())
                logger.info(f"YOLOv8 detected classes in frame: {sorted(detected_classes)}")
                self._logged_classes = True
            
            for r in results.boxes.data.tolist():
                x1, y1, x2, y2, conf, cls = r
                cls_idx = int(cls)
                class_name = results.names[cls_idx]
                original_conf = float(conf)
                
                # LIVE MOD: Tüm nesneler algılanacak - boyut/mesafe sınırı YOK
                if self.mode == "live_analysis":
                    # Tüm detections kabul et - sınır yok
                    pass
                else:
                    # VIDEO UPLOAD MOD: Orjinal filtreleme (DEĞİŞMEZ)
                    # Boyut kontrolü (opsiyonel, orjinal kodda yoksa hiçbir şey yapma)
                    pass
                
                # Map to dangerous object categories (with false positive filtering)
                mapped_class = self._map_to_dangerous_object(class_name, original_conf, [float(x1), float(y1), float(x2), float(y2)])
                
                # Calibrate confidence
                calibrated = self._calibrate_conf(original_conf)
                
                # Determine threshold based on mode and mapped class
                if self.mode == "live_analysis":
                    thr = self.confidence_threshold
                else:
                    # VIDEO UPLOAD MOD: Aggressive threshold lowering for weapons
                    # Check if mapped class is a dangerous object
                    if mapped_class in ['gun', 'weapon', 'knife', 'pistol', 'rifle', 'firearm', 'handgun']:
                        # Very low threshold for weapons (0.15) since YOLOv8 doesn't detect them well
                        thr = float(self.class_thresholds.get(mapped_class, 0.15))
                        logger.debug(f"Using very low threshold {thr} for dangerous object: {mapped_class} (original: {class_name}, conf: {original_conf:.3f})")
                    else:
                        # Check original class name for weapon keywords (even if not mapped)
                        class_lower = class_name.lower()
                        weapon_keywords = ['gun', 'pistol', 'rifle', 'firearm', 'weapon', 'knife', 'blade', 'handgun']
                        if any(keyword in class_lower for keyword in weapon_keywords):
                            # Potential weapon detected - use very low threshold
                            thr = 0.15
                            logger.debug(f"Potential weapon in original class '{class_name}', using threshold {thr} (conf: {original_conf:.3f})")
                            # Re-map to weapon category
                            if 'gun' in class_lower or 'pistol' in class_lower or 'firearm' in class_lower or 'handgun' in class_lower:
                                mapped_class = 'handgun'
                            elif 'knife' in class_lower or 'blade' in class_lower:
                                mapped_class = 'knife'
                            else:
                                mapped_class = 'weapon'
                        else:
                            # Regular object - use standard threshold
                            thr = float(self.class_thresholds.get(mapped_class, self.confidence_threshold))
                
                # Apply threshold filter
                if calibrated < thr:
                    # Log filtered detections for debugging (only for potential weapons)
                    if self.mode == "video_upload" and any(kw in class_name.lower() for kw in ['gun', 'pistol', 'rifle', 'firearm', 'weapon', 'knife', 'blade', 'handgun']):
                        logger.debug(f"Filtered detection: {class_name} (mapped: {mapped_class}, conf: {calibrated:.3f} < {thr:.3f})")
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
        weapon_keywords = ['gun', 'pistol', 'rifle', 'firearm', 'weapon', 'knife', 'blade', 'sword', 'handgun', 'revolver']
        for keyword in weapon_keywords:
            if keyword in class_name_lower:
                # Skip if it's a known false positive (only for knife)
                if class_name_lower in knife_false_positives and keyword == 'knife':
                    fp_config = knife_false_positives[class_name_lower]
                    if confidence >= fp_config.get('min_confidence', 0.5):
                        # Check aspect ratio and size if bbox available
                        if bbox is not None and len(bbox) >= 4:
                            width = bbox[2] - bbox[0]
                            height = bbox[3] - bbox[1]
                            if width > 0 and height > 0:
                                aspect_ratio = height / width
                                min_ar, max_ar = fp_config.get('aspect_ratio_range', (0.0, 10.0))
                                if min_ar <= aspect_ratio <= max_ar:
                                    # Matches false positive characteristics, skip
                                    logger.debug(f"Skipping false positive: {class_name} (confidence: {confidence:.3f}, aspect_ratio: {aspect_ratio:.2f})")
                                    continue
                
                # Map to specific weapon type based on keyword
                if keyword in ['gun', 'pistol', 'firearm', 'handgun', 'revolver']:
                    logger.debug(f"Found gun keyword '{keyword}' in {class_name}, mapping to handgun")
                    return 'handgun'
                elif keyword in ['knife', 'blade', 'sword']:
                    logger.debug(f"Found knife keyword '{keyword}' in {class_name}, mapping to knife")
                    return 'knife'
                else:
                    logger.debug(f"Found weapon keyword '{keyword}' in {class_name}, mapping to weapon")
                    return 'weapon'
        
        # SPECIAL CASE: YOLOv8 doesn't have handgun class, but some objects might be handguns
        # Check for objects that could be mistaken for handguns (cell phone, remote, etc.)
        # But only if confidence is low (high confidence = probably not a handgun)
        if confidence < 0.4:  # Low confidence detection
            handgun_like_objects = ['cell phone', 'remote', 'hair drier']
            if class_name_lower in handgun_like_objects:
                # Check aspect ratio - handguns are typically more rectangular
                if bbox is not None and len(bbox) >= 4:
                    width = bbox[2] - bbox[0]
                    height = bbox[3] - bbox[1]
                    if width > 0 and height > 0:
                        aspect_ratio = height / width
                        # Handguns are typically more horizontal (width > height)
                        if aspect_ratio < 0.8:  # Width is greater than height
                            logger.debug(f"Low confidence '{class_name}' with handgun-like aspect ratio, checking as potential handgun")
                            # Don't map directly, but will be checked in process_frame with lower threshold
                    
        # If not a dangerous object, return original class
        return class_name
    
    def _calculate_risk_level(self, class_name: str, confidence: float) -> str:
        """Calculate risk level based on object type and confidence"""
        high_risk_objects = ['handgun', 'gun', 'knife', 'weapon', 'pistol', 'rifle', 'firearm', 'machete', 'axe']  # Added handgun
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

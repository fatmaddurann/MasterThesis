import cv2
import numpy as np
from ultralytics import YOLO
import torch
from typing import Tuple, List, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

class ObjectDetector:
    def __init__(self):
        try:
            # Use YOLOv8n for faster inference
            model_path = os.path.join(os.path.dirname(__file__), 'yolov8n.pt')
            if not os.path.exists(model_path):
                logger.info("Downloading YOLOv8n model...")
                self.model = YOLO('yolov8n.pt')
                self.model.save(model_path)
            else:
                self.model = YOLO(model_path)
            
            # Simple tracking system
            self.tracked_objects = {}
            self.next_track_id = 0
            
            # Optimized model parameters
            self.conf_threshold = 0.45  # Lowered for better recall
            self.iou_threshold = 0.5   # Increased for better precision
            
            # Enhanced temporal consistency
            self.frame_history = []
            self.history_size = 10     # Increased history size
            
            # Tracking parameters
            self.min_tracking_confidence = 0.3
            self.max_tracking_age = 30  # frames
            self.min_tracking_hits = 3
            
            # Behavior analysis parameters
            self.behavior_history = {}
            self.min_behavior_frames = 10
            self.velocity_threshold = 5.0  # pixels per frame
            self.interaction_distance = 100  # pixels
            
            # Anomaly detection parameters
            self.anomaly_threshold = 0.8
            self.anomaly_window = 30  # frames
            self.anomaly_scores = []
            
            logger.info(f"Model loaded successfully on {self.model.device}")
            
        except Exception as e:
            logger.error(f"Error initializing detector: {str(e)}")
            raise

    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Apply enhanced preprocessing to improve frame quality"""
        try:
            # Convert to float32
            frame_float = frame.astype(np.float32) / 255.0
            
            # Apply adaptive contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            lab = cv2.cvtColor(frame_float, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            cl = clahe.apply(l)
            enhanced_lab = cv2.merge((cl, a, b))
            frame_contrast = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            
            # Apply advanced noise reduction
            frame_denoised = cv2.fastNlMeansDenoisingColored(
                frame_contrast,
                None,
                h=15,  # Increased filter strength
                hColor=15,
                templateWindowSize=7,
                searchWindowSize=21
            )
            
            # Apply sharpening
            kernel = np.array([[-1,-1,-1],
                             [-1, 9,-1],
                             [-1,-1,-1]])
            frame_sharpened = cv2.filter2D(frame_denoised, -1, kernel)
            
            return frame_sharpened
            
        except Exception as e:
            logger.error(f"Error in frame preprocessing: {str(e)}")
            return frame

    def process_video_frame(self, frame: np.ndarray) -> Tuple[List[Dict[str, Any]], np.ndarray]:
        """Process a single video frame with enhanced detection, tracking, and behavior analysis"""
        try:
            # Preprocess frame
            processed_frame = self.preprocess_frame(frame)
            
            # Run YOLOv8 detection with optimized parameters
            results = self.model(
                processed_frame,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                device='cuda' if torch.cuda.is_available() else 'cpu',
                verbose=False
            )
            
            # Extract and process detections
            detections = []
            annotated_frame = frame.copy()
            
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Get class and confidence
                    cls = int(box.cls[0].item())
                    conf = float(box.conf[0].item())
                    class_name = r.names[cls]
                    
                    # Apply temporal consistency and tracking
                    if self._check_temporal_consistency(x1, y1, x2, y2, class_name, conf):
                        detection = {
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'class_name': class_name,
                            'confidence': conf,
                            'track_id': self._get_track_id(x1, y1, x2, y2, class_name)
                        }
                        detections.append(detection)
                        
                        # Draw detection with tracking info
                        color = self._get_track_color(detection['track_id'])
                        cv2.rectangle(
                            annotated_frame,
                            (int(x1), int(y1)),
                            (int(x2), int(y2)),
                            color,
                            2
                        )
                        cv2.putText(
                            annotated_frame,
                            f'{class_name} {detection["track_id"]}: {conf:.2f}',
                            (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            color,
                            2
                        )
            
            # Update frame history and tracking
            self._update_frame_history(detections)
            self._update_tracking(detections)
            
            # Analyze behaviors and detect anomalies
            behaviors = self._analyze_behaviors(detections)
            anomalies = self._detect_anomalies(detections, behaviors)
            
            # Add behavior and anomaly information to detections
            for detection in detections:
                track_id = detection['track_id']
                if track_id in behaviors:
                    detection['behavior'] = behaviors[track_id]
                if track_id in anomalies:
                    detection['anomaly_score'] = anomalies[track_id]
            
            # Draw detections with behavior and anomaly information
            for detection in detections:
                color = self._get_track_color(detection['track_id'])
                x1, y1, x2, y2 = detection['bbox']
                
                # Draw bounding box
                cv2.rectangle(
                    annotated_frame,
                    (x1, y1),
                    (x2, y2),
                    color,
                    2
                )
                
                # Prepare label with behavior and anomaly information
                label_parts = [f"{detection['class_name']} {detection['track_id']}: {detection['confidence']:.2f}"]
                if 'behavior' in detection:
                    label_parts.append(f"Behavior: {detection['behavior']}")
                if 'anomaly_score' in detection and detection['anomaly_score'] > self.anomaly_threshold:
                    label_parts.append(f"Anomaly: {detection['anomaly_score']:.2f}")
                
                label = " | ".join(label_parts)
                
                # Draw label with background
                (label_width, label_height), _ = cv2.getTextSize(
                    label,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    1
                )
                cv2.rectangle(
                    annotated_frame,
                    (x1, y1 - label_height - 10),
                    (x1 + label_width, y1),
                    color,
                    -1
                )
                cv2.putText(
                    annotated_frame,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    1
                )
            
            return detections, annotated_frame
            
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            return [], frame

    def _check_temporal_consistency(self, x1: float, y1: float, x2: float, y2: float,
                                  class_name: str, conf: float) -> bool:
        """Check if detection is consistent with previous frames"""
        if not self.frame_history:
            return True
            
        # Check if similar detection exists in previous frames
        for prev_detections in self.frame_history:
            for prev_det in prev_detections:
                if prev_det['class_name'] == class_name:
                    prev_box = prev_det['bbox']
                    
                    # Calculate IoU with previous detection
                    iou = self._calculate_iou(
                        [x1, y1, x2, y2],
                        prev_box
                    )
                    
                    # If similar detection exists, require higher confidence
                    if iou > 0.3:
                        return conf > (self.conf_threshold * 0.8)
                        
        # If no similar detection, use standard confidence threshold
        return conf > self.conf_threshold

    def _calculate_iou(self, box1: List[float], box2: List[float]) -> float:
        """Calculate Intersection over Union between two boxes"""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        return intersection / (area1 + area2 - intersection)

    def _update_frame_history(self, detections: List[Dict[str, Any]]):
        """Update frame history for temporal consistency checking"""
        self.frame_history.append(detections)
        if len(self.frame_history) > self.history_size:
            self.frame_history.pop(0)

    def _get_track_id(self, x1: float, y1: float, x2: float, y2: float, class_name: str) -> int:
        """Assign a track ID to a detection using simple IoU-based tracking"""
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # Check if this detection matches any existing track
        for track_id, track_info in self.tracked_objects.items():
            if track_info['class_name'] == class_name:
                prev_center_x = (track_info['bbox'][0] + track_info['bbox'][2]) / 2
                prev_center_y = (track_info['bbox'][1] + track_info['bbox'][3]) / 2
                
                # Calculate distance between centers
                distance = np.sqrt((center_x - prev_center_x)**2 + (center_y - prev_center_y)**2)
                
                # If centers are close enough, update track
                if distance < self.interaction_distance:
                    track_info['bbox'] = [x1, y1, x2, y2]
                    track_info['age'] = 0
                    return track_id
        
        # If no match found, create new track
        track_id = self.next_track_id
        self.next_track_id += 1
        
        self.tracked_objects[track_id] = {
            'bbox': [x1, y1, x2, y2],
            'class_name': class_name,
            'age': 0
        }
        
        return track_id

    def _get_track_color(self, track_id: int) -> Tuple[int, int, int]:
        """Get consistent color for a track ID"""
        if track_id == -1:
            return (0, 255, 0)  # Default green
            
        # Generate consistent color based on track ID
        np.random.seed(track_id)
        color = tuple(map(int, np.random.randint(0, 255, 3)))
        np.random.seed(None)
        return color

    def _update_tracking(self, detections: List[Dict[str, Any]]):
        """Update tracking information for all objects"""
        # Age all tracks
        for track_info in self.tracked_objects.values():
            track_info['age'] += 1
        
        # Remove old tracks
        self.tracked_objects = {
            track_id: track_info
            for track_id, track_info in self.tracked_objects.items()
            if track_info['age'] < self.max_tracking_age
        }

    def detect_objects(self, frame: np.ndarray) -> list:
        try:
            results = self.model(frame, verbose=False)[0]
            detections = []
            
            for r in results.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = r
                detections.append({
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'confidence': float(score),
                    'class_id': int(class_id),
                    'class_name': results.names[int(class_id)]
                })
            
            return detections
        except Exception as e:
            print("Error during detection:", str(e))
            return []

    def draw_detections(self, frame: np.ndarray, detections: list) -> np.ndarray:
        try:
            annotated_frame = frame.copy()
            
            for detection in detections:
                x1, y1, x2, y2 = [int(coord) for coord in detection['bbox']]
                class_name = detection['class_name']
                confidence = detection['confidence']
                
                # Draw bounding box
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw label
                label = f"{class_name}: {confidence:.2f}"
                (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(annotated_frame, (x1, y1 - label_height - 10), (x1 + label_width, y1), (0, 255, 0), -1)
                cv2.putText(annotated_frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
            return annotated_frame
        except Exception as e:
            print("Error drawing detections:", str(e))
            return frame

    def _analyze_behaviors(self, detections: List[Dict[str, Any]]) -> Dict[int, str]:
        """Analyze behaviors of tracked objects"""
        behaviors = {}
        
        for detection in detections:
            track_id = detection['track_id']
            if track_id not in self.behavior_history:
                self.behavior_history[track_id] = {
                    'positions': [],
                    'velocities': [],
                    'interactions': []
                }
            
            # Update position history
            center_x = (detection['bbox'][0] + detection['bbox'][2]) / 2
            center_y = (detection['bbox'][1] + detection['bbox'][3]) / 2
            self.behavior_history[track_id]['positions'].append((center_x, center_y))
            
            # Calculate velocity
            if len(self.behavior_history[track_id]['positions']) > 1:
                prev_x, prev_y = self.behavior_history[track_id]['positions'][-2]
                velocity = np.sqrt((center_x - prev_x)**2 + (center_y - prev_y)**2)
                self.behavior_history[track_id]['velocities'].append(velocity)
            
            # Check for interactions with other objects
            for other_detection in detections:
                if other_detection['track_id'] != track_id:
                    other_center_x = (other_detection['bbox'][0] + other_detection['bbox'][2]) / 2
                    other_center_y = (other_detection['bbox'][1] + other_detection['bbox'][3]) / 2
                    distance = np.sqrt((center_x - other_center_x)**2 + (center_y - other_center_y)**2)
                    
                    if distance < self.interaction_distance:
                        self.behavior_history[track_id]['interactions'].append(other_detection['track_id'])
            
            # Determine behavior based on history
            if len(self.behavior_history[track_id]['positions']) >= self.min_behavior_frames:
                behavior = self._determine_behavior(track_id)
                behaviors[track_id] = behavior
            
            # Clean up old history
            if len(self.behavior_history[track_id]['positions']) > self.anomaly_window:
                self.behavior_history[track_id]['positions'].pop(0)
                if self.behavior_history[track_id]['velocities']:
                    self.behavior_history[track_id]['velocities'].pop(0)
                if self.behavior_history[track_id]['interactions']:
                    self.behavior_history[track_id]['interactions'].pop(0)
        
        return behaviors

    def _determine_behavior(self, track_id: int) -> str:
        """Determine behavior based on object's history"""
        history = self.behavior_history[track_id]
        
        if not history['velocities']:
            return "stationary"
        
        # Calculate average velocity
        avg_velocity = np.mean(history['velocities'])
        
        # Calculate movement pattern
        positions = np.array(history['positions'])
        if len(positions) > 2:
            # Calculate direction changes
            directions = np.diff(positions, axis=0)
            direction_changes = np.arccos(
                np.clip(
                    np.sum(directions[:-1] * directions[1:], axis=1) /
                    (np.linalg.norm(directions[:-1], axis=1) * np.linalg.norm(directions[1:], axis=1)),
                    -1.0,
                    1.0
                )
            )
            avg_direction_change = np.mean(direction_changes)
        else:
            avg_direction_change = 0
        
        # Determine behavior based on velocity and movement pattern
        if avg_velocity < self.velocity_threshold:
            return "stationary"
        elif avg_direction_change > np.pi/2:
            return "erratic"
        elif len(history['interactions']) > 0:
            return "interacting"
        else:
            return "moving"

    def _detect_anomalies(self, detections: List[Dict[str, Any]], behaviors: Dict[int, str]) -> Dict[int, float]:
        """Detect anomalies in object behaviors"""
        anomalies = {}
        
        for detection in detections:
            track_id = detection['track_id']
            if track_id not in self.behavior_history:
                continue
            
            history = self.behavior_history[track_id]
            if len(history['positions']) < self.min_behavior_frames:
                continue
            
            # Calculate anomaly score based on multiple factors
            anomaly_score = 0.0
            
            # 1. Velocity anomaly
            if history['velocities']:
                avg_velocity = np.mean(history['velocities'])
                velocity_std = np.std(history['velocities'])
                if velocity_std > 0:
                    velocity_zscore = abs(avg_velocity - np.mean(history['velocities'])) / velocity_std
                    anomaly_score += min(velocity_zscore / 3, 1.0)
            
            # 2. Behavior anomaly
            if track_id in behaviors:
                if behaviors[track_id] == "erratic":
                    anomaly_score += 0.3
                elif behaviors[track_id] == "interacting":
                    anomaly_score += 0.2
            
            # 3. Interaction anomaly
            if len(history['interactions']) > 2:
                anomaly_score += 0.2
            
            # 4. Position anomaly
            positions = np.array(history['positions'])
            if len(positions) > 2:
                position_std = np.std(positions, axis=0)
                if np.mean(position_std) > 100:  # Large position variation
                    anomaly_score += 0.3
            
            # Normalize anomaly score
            anomaly_score = min(anomaly_score, 1.0)
            anomalies[track_id] = anomaly_score
            
            # Update anomaly history
            self.anomaly_scores.append(anomaly_score)
            if len(self.anomaly_scores) > self.anomaly_window:
                self.anomaly_scores.pop(0)
        
        return anomalies
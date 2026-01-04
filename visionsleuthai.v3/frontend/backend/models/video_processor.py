from typing import Any, Dict, List, Tuple
import os
import json
import numpy as np


def _iou(box_a: List[float], box_b: List[float]) -> float:
    x1 = max(box_a[0], box_b[0])
    y1 = max(box_a[1], box_b[1])
    x2 = min(box_a[2], box_b[2])
    y2 = min(box_a[3], box_b[3])
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    area_a = max(0.0, box_a[2] - box_a[0]) * max(0.0, box_a[3] - box_a[1])
    area_b = max(0.0, box_b[2] - box_b[0]) * max(0.0, box_b[3] - box_b[1])
    denom = area_a + area_b - inter
    return inter / denom if denom > 0 else 0.0


class VideoProcessor:
    def __init__(self, model, mode: str = "video_upload"):
        """
        Initialize VideoProcessor with mode parameter.
        
        Args:
            model: CrimeDetectionModel instance
            mode: "video_upload" (default, no changes) or "live_analysis" (all improvements active)
        """
        self.model = model
        self.mode = mode
        self.previous_detections: List[Dict[str, Any]] = []
        # EMA katsayısı env'den konfigüre edilebilir
        try:
            self.smoothing_alpha = float(os.getenv("SMOOTHING_ALPHA", "0.6"))
        except Exception:
            self.smoothing_alpha = 0.6
        # Sınıf bazlı risk ağırlıkları env üzerinden JSON ile konfigüre edilebilir
        default_weights: Dict[str, float] = {
            "gun": 1.0,
            "knife": 0.9,
            "weapon": 0.95,
            "pistol": 1.0,
            "rifle": 1.0,
            "firearm": 1.0,
            "machete": 0.95,
            "axe": 0.9,
            "scissors": 0.5,
            "bottle": 0.3,
            "hammer": 0.5,
            "crowbar": 0.6,
            "baseball_bat": 0.7,
        }
        try:
            risk_env = os.getenv("RISK_CLASS_WEIGHTS", "")
            self.class_risk_weight = {**default_weights, **(json.loads(risk_env) if risk_env else {})}
        except Exception:
            self.class_risk_weight = default_weights
        # Basit ID takibi parametreleri
        self.iou_match_threshold: float = float(os.getenv("TRACK_IOU_THRESHOLD", "0.3"))
        self.next_track_id: int = 1

    def _smooth_confidence(self, current: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.previous_detections:
            return current

        smoothed: List[Dict[str, Any]] = []
        used_prev = [False] * len(self.previous_detections)
        for det in current:
            best_iou = 0.0
            best_idx = -1
            for i, prev in enumerate(self.previous_detections):
                iou = _iou(det["bbox"], prev["bbox"])  # type: ignore
                if iou > best_iou:
                    best_iou = iou
                    best_idx = i
            if best_idx >= 0 and best_iou >= self.iou_match_threshold:
                prev = self.previous_detections[best_idx]
                used_prev[best_idx] = True
                # EMA: yeni = a*eski + (1-a)*mevcut
                prev_conf = float(prev.get("confidence", 0.0))
                cur_conf = float(det.get("confidence", 0.0))
                det["confidence"] = self.smoothing_alpha * prev_conf + (1.0 - self.smoothing_alpha) * cur_conf
                # Track ID'yi taşı
                if "track_id" in prev:
                    det["track_id"] = prev["track_id"]
                smoothed.append(det)
            else:
                smoothed.append(det)
        return smoothed

    def _assess_risk(self, det: Dict[str, Any], frame_shape: Tuple[int, int, int]) -> float:
        class_name = str(det.get("class_name", "")).lower()
        conf = float(det.get("confidence", 0.0))  # 0..1
        bbox = det.get("bbox", [0.0, 0.0, 0.0, 0.0])
        h, w = frame_shape[0], frame_shape[1]
        area = max(0.0, (bbox[2] - bbox[0])) * max(0.0, (bbox[3] - bbox[1]))
        frame_area = max(1.0, float(w * h))
        area_ratio = min(1.0, area / frame_area)

        # Sınıf ağırlığı
        base_w = 0.4
        w_class = self.class_risk_weight.get(class_name, 0.2)
        # Yakınlık/alan etkisi
        w_area = 0.3
        # Güven etkisi
        w_conf = 0.3

        raw_score = base_w + w_class * 1.0 + w_area * area_ratio + w_conf * conf
        # 0..1 aralığına sıkıştır
        return max(0.0, min(1.0, raw_score))

    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        # Model çerçeve işleme - ARTIK TRACKING MODEL İÇİNDE YAPILIYOR
        detections, _annotated = self.model.process_frame(frame)

        # Risk skoru hesapla ve etiketle
        enriched: List[Dict[str, Any]] = []
        for det in detections:
            if isinstance(det, dict):
                risk = self._assess_risk(det, frame.shape)
                det_out = {
                    "type": det.get("class_name", "unknown"),
                    "class_name": det.get("class_name", "unknown"),
                    "confidence": float(det.get("confidence", 0.0)),
                    "bbox": det.get("bbox", [0.0, 0.0, 0.0, 0.0]),
                    "risk_score": risk,
                    "track_id": det.get("track_id", 0) # Modelden gelen ID'yi kullan
                }
                enriched.append(det_out)
            else:
                # Eğer det dictionary değilse, logla ve atla
                print(f"Warning: Detection is not a dictionary: {type(det)} - {det}")
                continue

        # LIVE MOD: Tehlikeli nesne + person durumunda güven düşürme
        if self.mode == "live_analysis":
            enriched = self._apply_risk_based_confidence_adjustment(enriched)
        
        # Basit şüpheli etkileşim örneği: yüksek riskli bir nesne varsa bildir
        suspicious_interactions: List[Dict[str, Any]] = []
        high_risk = [d for d in enriched if d["risk_score"] >= 0.8]
        if high_risk:
            suspicious_interactions.append({
                "type": "high_risk_object_detected",
                "count": len(high_risk),
                "max_risk": max(d["risk_score"] for d in high_risk),
            })

        # Bir sonraki kare için durumu güncelle
        self.previous_detections = [
            {
                "bbox": d.get("bbox", [0.0, 0.0, 0.0, 0.0]),
                "confidence": d.get("confidence", 0.0),
                "track_id": d.get("track_id"),
            }
            for d in enriched
        ]

        # Kare ortalama güven skoru (video_analysis'taki kullanım için)
        avg_conf = float(np.mean([d.get("confidence", 0.0) for d in enriched])) if enriched else 0.0

        return {
            "detections": enriched,
            "suspicious_interactions": suspicious_interactions,
            "confidence": avg_conf,
        }

    def _apply_risk_based_confidence_adjustment(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        LIVE MOD: Tehlikeli nesne + person durumunda güveni düşür.
        
        Risk seviyeleri:
        - YÜKSEK RİSK (gun, knife, weapon, pistol): %50 güven düşüşü
        - ORTA RİSK (scissors, hammer, bat): %30 güven düşüşü
        - DÜŞÜK RİSK (bottle, tool): %15 güven düşüşü
        """
        if self.mode != "live_analysis":
            return detections
        
        # Risk seviyesi belirleme
        high_risk_objects = ['gun', 'knife', 'weapon', 'pistol', 'rifle', 'firearm', 'machete']
        medium_risk_objects = ['scissors', 'hammer', 'baseball_bat', 'crowbar', 'axe']
        low_risk_objects = ['bottle', 'tool']
        
        # Person ve tehlikeli nesne tespitleri
        persons = [d for d in detections if d.get("class_name", "").lower() in ["person", "people"]]
        dangerous_objects = [
            d for d in detections 
            if d.get("class_name", "").lower() in high_risk_objects + medium_risk_objects + low_risk_objects
        ]
        
        # Eğer person ve tehlikeli nesne birlikte varsa
        if persons and dangerous_objects:
            for person in persons:
                person_bbox = person.get("bbox", [0, 0, 0, 0])
                
                # Check for overlap or extreme proximity
                for danger_obj in dangerous_objects:
                    danger_bbox = danger_obj.get("bbox", [0, 0, 0, 0])
                    
                    # Calculate IoU-like overlap or distance between centers
                    iou = _iou(person_bbox, danger_bbox)
                    
                    # If person is holding or very close to the object (overlap > 0 or distance is small)
                    if iou > 0:
                        danger_class = danger_obj.get("class_name", "").lower()
                        original_conf = person.get("confidence", 0.0)
                        
                        # Risk increase for the whole frame / person
                        risk_ratio = 0.6 if danger_class in high_risk_objects else 0.3
                        
                        # Boost detection confidence for the dangerous object if it's within a person box
                        danger_obj["confidence"] = min(0.99, danger_obj["confidence"] * 1.2)
                        
                        # Lower security score (confidence) for the person
                        adjusted_conf = original_conf * (1 - risk_ratio)
                        person["confidence"] = max(0.0, adjusted_conf)
                        person["risk_adjusted"] = True
                        person["risk_reason"] = f"Suspected interaction with {danger_class}"
                        person["security_score"] = adjusted_conf
        
        return detections
        
        return detections

    def process(self, video_path: str) -> Dict[str, Any]:
        # Mevcut basit iskelet; video bazlı işleme üst seviye akışta yapılmakta
        return {
            "status": "success",
            "message": f"Video {video_path} processing started",
        }

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


from models.threat_analyzer import ThreatAnalyzer

class VideoProcessor:
    def __init__(self, model, mode: str = "video_upload"):
        self.model = model
        self.mode = mode
        self.threat_analyzer = ThreatAnalyzer(iou_threshold=0.15)
        # ... (diğer init kodları aynı kalacak)
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
        # Model çerçeve işleme - ByteTrack ile track_id dahil gelir
        detections, _annotated = self.model.process_frame(frame)

        # Temel zenginleştirme (Risk skoru hesaplama)
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
                    "track_id": det.get("track_id", 0)
                }
                enriched.append(det_out)

        # TEZİN ÖZGÜN MANTIĞI: ThreatAnalyzer ile bağlam duyarlı analiz
        threat_results = self.threat_analyzer.analyze(enriched)
        
        # Analiz sonuçlarını ana tespit listesine işle
        for threat in threat_results:
            for det in enriched:
                # Bbox eşleşmesi üzerinden ek bilgileri aktar
                if det['bbox'] == threat['bbox']:
                    det['alert_level'] = threat.get('alert_level')
                    det['event_type'] = threat.get('event_type')
                    det['associated_person_id'] = threat.get('associated_person_id')
                    # Güvenlik puanını güncelle (silah taşıyorsa düşür)
                    if threat.get('alert_level') == "CRITICAL":
                        det['security_score'] = det['confidence'] * 0.4

        # Ortalama güven skoru
        avg_conf = float(np.mean([d.get("confidence", 0.0) for d in enriched])) if enriched else 0.0

        return {
            "detections": enriched,
            "suspicious_interactions": threat_results, # Adli rapora giden kritik veri
            "confidence": avg_conf,
        }

    def process(self, video_path: str) -> Dict[str, Any]:
        # Mevcut basit iskelet; video bazlı işleme üst seviye akışta yapılmakta
        return {
            "status": "success",
            "message": f"Video {video_path} processing started",
        }

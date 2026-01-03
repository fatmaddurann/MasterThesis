import numpy as np
from typing import List, Dict, Any

class ThreatAnalyzer:
    def __init__(self, iou_threshold: float = 0.1):
        self.iou_threshold = iou_threshold
        # Sert Negatif Filtresi (Step 4)
        self.non_threat_objects = ['cell phone', 'smartphone', 'remote', 'drill']
        self.lethal_weapons = ['handgun', 'rifle', 'knife', 'gun', 'weapon', 'pistol']

    def _calculate_iou(self, boxA, boxB):
        # Kesişim hesaplama (Step 3 için yardımcı fonksiyon)
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)
        
        # Area of boxes
        areaA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        areaB = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        
        # Handle zero area
        if areaA + areaB - interArea <= 0:
            return 0
            
        return interArea / float(areaA + areaB - interArea)

    def analyze(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        persons = [d for d in detections if d.get('class_name', '').lower() in ['person', 'people']]
        threats = [d for d in detections if d.get('class_name', '').lower() in self.lethal_weapons]
        hard_negatives = [d for d in detections if d.get('class_name', '').lower() in self.non_threat_objects]

        results = []

        for threat in threats:
            threat_box = threat['bbox']
            is_armed_interaction = False
            
            # Step 4: Sert Negatif Kontrolü
            is_false_positive = False
            for neg in hard_negatives:
                if self._calculate_iou(threat_box, neg['bbox']) > 0.5 and neg['confidence'] > threat['confidence']:
                    threat['status'] = "False Positive Filtered"
                    is_false_positive = True
                    break
            
            if is_false_positive:
                continue

            # Step 3: İnsan-Nesne Etkileşimi
            for person in persons:
                overlap = self._calculate_iou(threat_box, person['bbox'])
                
                # Check for containment or high overlap
                if overlap > self.iou_threshold:
                    # Nesne insanın içinde veya çok yakınında -> Silahlı Şüpheli
                    threat['alert_level'] = "CRITICAL"
                    threat['event_type'] = "Armed Suspect Alert"
                    threat['associated_person_id'] = person.get('track_id')
                    is_armed_interaction = True
                    break
            
            if not is_armed_interaction:
                # Nesne izole durumda -> Sahipsiz Silah
                threat['alert_level'] = "WARNING"
                threat['event_type'] = "Unattended Weapon Warning"

            results.append(threat)
            
        return results


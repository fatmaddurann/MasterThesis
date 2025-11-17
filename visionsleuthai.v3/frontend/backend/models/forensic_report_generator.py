"""
Forensic Report Generator Module

This module generates professional forensic-standard reports from detection results.
It does NOT modify any detection values, scores, or thresholds - only interprets
the results in forensic style.

Author: Forensic AI Crime Detection System
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ForensicReportGenerator:
    """
    Generates professional forensic reports from detection results.
    
    This class takes detection output as input and produces advanced
    forensic-style reports without modifying any detection values.
    """
    
    def __init__(self):
        """Initialize the forensic report generator."""
        self.low_confidence_threshold = 0.50
        
    def generate_report(self, detection_data: Dict[str, Any]) -> str:
        """
        Generate a complete forensic report from detection data.
        
        Args:
            detection_data: Dictionary containing:
                - timestamp: ISO format timestamp string
                - detections: List of detection dictionaries with:
                    - label/type/class_name: Object class name
                    - confidence: Confidence score (0.0-1.0)
                    - bbox: Bounding box coordinates [x1, y1, x2, y2]
                    - (optional) risk_level: Risk level string
                    - (optional) risk_score: Risk score (0.0-1.0)
        
        Returns:
            Formatted multi-section forensic report as plain text.
        """
        try:
            timestamp = detection_data.get("timestamp", datetime.utcnow().isoformat())
            detections = detection_data.get("detections", [])
            
            # Normalize detection format
            normalized_detections = self._normalize_detections(detections)
            
            # Generate each section
            report_sections = []
            
            report_sections.append(self._generate_executive_summary(normalized_detections, timestamp))
            report_sections.append(self._generate_forensic_observation_log(normalized_detections, timestamp))
            report_sections.append(self._generate_behavioral_interpretation(normalized_detections))
            report_sections.append(self._generate_evidential_confidence_analysis(normalized_detections))
            report_sections.append(self._generate_scene_contextualization(normalized_detections))
            report_sections.append(self._generate_limitations_disclaimer())
            
            # Combine all sections
            full_report = "\n\n".join(report_sections)
            
            return full_report
            
        except Exception as e:
            logger.error(f"Error generating forensic report: {str(e)}")
            return self._generate_error_report(str(e))
    
    def _normalize_detections(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize detection format to ensure consistent field names.
        
        Handles variations: 'label', 'type', 'class_name' -> 'class_name'
        """
        normalized = []
        for det in detections:
            if not isinstance(det, dict):
                continue
                
            # Normalize class name field
            class_name = (
                det.get("label") or 
                det.get("type") or 
                det.get("class_name") or 
                "unknown"
            )
            
            normalized_det = {
                "class_name": str(class_name),
                "confidence": float(det.get("confidence", 0.0)),
                "bbox": det.get("bbox", [0.0, 0.0, 0.0, 0.0]),
                "risk_level": det.get("risk_level", "Unknown"),
                "risk_score": float(det.get("risk_score", 0.0)),
            }
            
            # Preserve any additional fields
            for key, value in det.items():
                if key not in normalized_det:
                    normalized_det[key] = value
            
            normalized.append(normalized_det)
        
        return normalized
    
    def _generate_executive_summary(self, detections: List[Dict[str, Any]], timestamp: str) -> str:
        """Generate Executive Summary section."""
        section = "=" * 80
        section += "\n1. EXECUTIVE SUMMARY\n"
        section += "=" * 80
        
        if not detections:
            section += "\nThe automated analysis system processed the submitted evidence at "
            section += f"{timestamp}.\n\n"
            section += "No objects or activities meeting the detection criteria were identified "
            section += "during the analysis period. The scene was assessed as presenting minimal "
            section += "observable risk indicators based on the available visual evidence.\n"
            return section
        
        # Count detections by type
        detection_counts = {}
        high_confidence_detections = []
        dangerous_objects = []
        
        for det in detections:
            class_name = det["class_name"]
            confidence = det["confidence"]
            
            detection_counts[class_name] = detection_counts.get(class_name, 0) + 1
            
            if confidence >= 0.70:
                high_confidence_detections.append(det)
            
            if self._is_dangerous_object(class_name):
                dangerous_objects.append(det)
        
        section += f"\nThe automated forensic analysis system processed the submitted evidence "
        section += f"at {timestamp}. The analysis identified {len(detections)} distinct detection "
        section += f"event(s) across {len(detection_counts)} unique object class(es).\n\n"
        
        if dangerous_objects:
            section += f"Of particular forensic significance, {len(dangerous_objects)} detection(s) "
            section += "corresponded to objects classified as potentially dangerous or "
            section += "threat-related. "
        
        if high_confidence_detections:
            section += f"{len(high_confidence_detections)} detection(s) were recorded with "
            section += "confidence scores exceeding 0.70, indicating strong model certainty "
            section += "regarding the identified classifications.\n"
        else:
            section += "The confidence scores associated with the detections suggest moderate "
            section += "to low certainty, warranting careful expert review.\n"
        
        section += "\nThis summary presents the initial automated findings. Detailed analysis "
        section += "and expert interpretation are provided in subsequent sections of this report.\n"
        
        return section
    
    def _generate_forensic_observation_log(self, detections: List[Dict[str, Any]], timestamp: str) -> str:
        """Generate Forensic Observation Log section."""
        section = "=" * 80
        section += "\n2. FORENSIC OBSERVATION LOG\n"
        section += "=" * 80
        
        if not detections:
            section += "\nNo detections were recorded during the analysis period.\n"
            return section
        
        section += f"\nTimestamp of Analysis: {timestamp}\n"
        section += "\nThe following observations are based exclusively on the automated "
        section += "detection system output. No assumptions or interpretations beyond the "
        section += "model's direct output are included in this log.\n\n"
        section += "-" * 80 + "\n"
        
        for idx, det in enumerate(detections, 1):
            class_name = det["class_name"]
            confidence = det["confidence"]
            bbox = det["bbox"]
            risk_level = det.get("risk_level", "Not Assessed")
            
            section += f"\nObservation #{idx}:\n"
            section += f"  Object Class: {class_name}\n"
            section += f"  Detection Confidence: {confidence:.3f} ({confidence*100:.1f}%)\n"
            section += f"  Risk Level Classification: {risk_level}\n"
            
            if len(bbox) >= 4:
                x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                width = abs(x2 - x1)
                height = abs(y2 - y1)
                
                section += f"  Spatial Coordinates:\n"
                section += f"    - Bounding Box: [{x1:.1f}, {y1:.1f}, {x2:.1f}, {y2:.1f}]\n"
                section += f"    - Estimated Center: ({center_x:.1f}, {center_y:.1f})\n"
                section += f"    - Estimated Dimensions: {width:.1f} × {height:.1f} pixels\n"
            
            # Confidence-based qualification
            if confidence < self.low_confidence_threshold:
                section += f"  Note: This detection falls below the 0.50 confidence threshold "
                section += "and is classified as a low-confidence observation. Expert review "
                section += "is strongly recommended.\n"
            
            section += "\n" + "-" * 80 + "\n"
        
        section += "\nEnd of Observation Log\n"
        
        return section
    
    def _generate_behavioral_interpretation(self, detections: List[Dict[str, Any]]) -> str:
        """Generate Behavioral Interpretation & Threat Assessment section."""
        section = "=" * 80
        section += "\n3. BEHAVIORAL INTERPRETATION & THREAT ASSESSMENT\n"
        section += "=" * 80
        
        if not detections:
            section += "\nBased on the detected pattern, no significant behavioral indicators "
            section += "or threat-related objects were identified. The assessed risk level is: "
            section += "LOW.\n"
            return section
        
        # Analyze detections
        dangerous_objects = [d for d in detections if self._is_dangerous_object(d["class_name"])]
        persons = [d for d in detections if d["class_name"].lower() in ["person", "people"]]
        high_confidence_detections = [d for d in detections if d["confidence"] >= 0.70]
        
        # Determine overall risk level
        overall_risk = self._assess_overall_risk(detections)
        
        section += "\nBased on the detected pattern, the following interpretations are provided:\n\n"
        
        # Object presence analysis
        if dangerous_objects:
            section += f"Object Presence Analysis:\n"
            section += f"The system detected {len(dangerous_objects)} object(s) classified as "
            section += "potentially dangerous or threat-related. "
            
            dangerous_types = set(d["class_name"] for d in dangerous_objects)
            section += f"The detected object types include: {', '.join(sorted(dangerous_types))}.\n\n"
            
            # Analyze spatial relationships
            if persons and dangerous_objects:
                section += "Spatial Relationship Analysis:\n"
                section += "The detection output indicates the presence of both person(s) and "
                section += "potentially dangerous object(s) within the analyzed frame. "
                section += "Based on the detected pattern, spatial proximity between these "
                section += "entities cannot be definitively established from the automated "
                section += "analysis alone. Expert review of the spatial relationships is "
                section += "recommended.\n\n"
        
        # Behavioral indicators
        section += "Behavioral Indicators:\n"
        if high_confidence_detections:
            section += f"{len(high_confidence_detections)} detection(s) exhibited high confidence "
            section += "scores (≥0.70), suggesting strong model certainty. "
        
        if len(detections) > 1:
            section += f"The presence of multiple detections ({len(detections)} total) may indicate "
            section += "a complex scene requiring detailed examination.\n\n"
        else:
            section += "A single detection event was recorded, suggesting a relatively isolated "
            section += "observation.\n\n"
        
        # Threat assessment
        section += "Threat Assessment:\n"
        section += f"Based strictly on the detection output, the assessed risk level is: "
        section += f"{overall_risk.upper()}.\n\n"
        
        if overall_risk == "HIGH":
            section += "The combination of detected object types, confidence scores, and "
            section += "spatial indicators suggests elevated concern. However, this assessment "
            section += "is based solely on automated analysis and does not constitute definitive "
            section += "threat identification. Immediate expert review is recommended.\n"
        elif overall_risk == "MEDIUM":
            section += "The detection pattern suggests moderate concern. The presence of "
            section += "certain object classes or behavioral indicators warrants careful "
            section += "examination. Expert review is recommended to validate and contextualize "
            section += "these findings.\n"
        else:
            section += "The detection pattern suggests low immediate concern. However, all "
            section += "detections should be reviewed by qualified personnel to ensure "
            section += "appropriate contextualization.\n"
        
        section += "\nNote: This threat assessment is derived exclusively from the automated "
        section += "detection output and does not replace professional security or law "
        section += "enforcement evaluation.\n"
        
        return section
    
    def _generate_evidential_confidence_analysis(self, detections: List[Dict[str, Any]]) -> str:
        """Generate Evidential Confidence Analysis section."""
        section = "=" * 80
        section += "\n4. EVIDENTIAL CONFIDENCE ANALYSIS\n"
        section += "=" * 80
        
        if not detections:
            section += "\nNo detections were recorded; therefore, no confidence analysis is applicable.\n"
            return section
        
        # Calculate statistics
        confidences = [d["confidence"] for d in detections]
        avg_confidence = sum(confidences) / len(confidences)
        max_confidence = max(confidences)
        min_confidence = min(confidences)
        
        high_conf_count = sum(1 for c in confidences if c >= 0.80)
        medium_conf_count = sum(1 for c in confidences if 0.50 <= c < 0.80)
        low_conf_count = sum(1 for c in confidences if c < 0.50)
        
        section += "\nThe following analysis examines the confidence scores provided by the "
        section += "detection model. These scores represent the model's internal assessment "
        section += "of certainty regarding each classification.\n\n"
        
        section += "Confidence Score Statistics:\n"
        section += f"  - Total Detections: {len(detections)}\n"
        section += f"  - Average Confidence: {avg_confidence:.3f} ({avg_confidence*100:.1f}%)\n"
        section += f"  - Maximum Confidence: {max_confidence:.3f} ({max_confidence*100:.1f}%)\n"
        section += f"  - Minimum Confidence: {min_confidence:.3f} ({min_confidence*100:.1f}%)\n\n"
        
        section += "Confidence Distribution:\n"
        section += f"  - High Confidence (≥0.80): {high_conf_count} detection(s)\n"
        section += f"  - Medium Confidence (0.50-0.79): {medium_conf_count} detection(s)\n"
        section += f"  - Low Confidence (<0.50): {low_conf_count} detection(s)\n\n"
        
        # Interpret confidence scores
        section += "Forensic Interpretation of Confidence Scores:\n\n"
        
        if high_conf_count > 0:
            section += "High confidence scores (≥0.80) indicate strong model certainty. "
            section += "For example, a 0.87 confidence score suggests a strong indication "
            section += "that the detected object matches the identified class. However, "
            section += "even high confidence scores do not replace expert human review and "
            section += "should be considered as probabilistic assessments rather than "
            section += "definitive identifications.\n\n"
        
        if medium_conf_count > 0:
            section += "Medium confidence scores (0.50-0.79) indicate moderate model certainty. "
            section += "These detections warrant careful examination, as the model expresses "
            section += "some uncertainty. Expert review is recommended to validate these "
            section += "classifications and assess their evidentiary value.\n\n"
        
        if low_conf_count > 0:
            section += "Low confidence scores (<0.50) indicate weak model certainty. These "
            section += "detections are classified as low-confidence observations and should "
            section += "be treated with particular caution. They may represent false positives, "
            section += "ambiguous visual features, or objects at the edge of the model's "
            section += "classification capabilities. Expert review is essential for these cases.\n\n"
        
        # Individual detection confidence analysis
        section += "Individual Detection Confidence Analysis:\n"
        for idx, det in enumerate(detections, 1):
            conf = det["confidence"]
            class_name = det["class_name"]
            
            section += f"\n  Detection #{idx} ({class_name}):\n"
            section += f"    Confidence Score: {conf:.3f}\n"
            
            if conf >= 0.80:
                section += f"    Interpretation: High confidence. The model indicates strong "
                section += f"certainty ({(conf*100):.1f}%) that this detection corresponds to "
                section += f"the identified class. This represents a strong indication but does "
                section += f"not constitute definitive proof.\n"
            elif conf >= 0.50:
                section += f"    Interpretation: Medium confidence. The model indicates "
                section += f"moderate certainty ({(conf*100):.1f}%) regarding this classification. "
                section += f"Expert review is recommended to validate this detection.\n"
            else:
                section += f"    Interpretation: Low confidence. The model indicates weak "
                section += f"certainty ({(conf*100):.1f}%) for this detection. This observation "
                section += f"should be treated with caution and requires expert validation.\n"
        
        section += "\nImportant Note: Confidence scores reflect the model's internal assessment "
        section += "and are not equivalent to legal standards of proof or expert opinion. "
        section += "All detections, regardless of confidence level, require appropriate "
        section += "professional review.\n"
        
        return section
    
    def _generate_scene_contextualization(self, detections: List[Dict[str, Any]]) -> str:
        """Generate Scene Contextualization section."""
        section = "=" * 80
        section += "\n5. SCENE CONTEXTUALIZATION\n"
        section += "=" * 80
        
        if not detections:
            section += "\nNo detections were recorded; therefore, no spatial analysis is applicable.\n"
            return section
        
        section += "\nThis section describes the spatial relationships among detected objects "
        section += "based exclusively on the bounding box coordinates provided by the detection "
        section += "system. No speculative interpretations are included.\n\n"
        
        # Group detections by type
        persons = [d for d in detections if d["class_name"].lower() in ["person", "people"]]
        dangerous_objects = [d for d in detections if self._is_dangerous_object(d["class_name"])]
        other_objects = [d for d in detections if d not in persons and d not in dangerous_objects]
        
        section += "Detected Entity Summary:\n"
        section += f"  - Person(s): {len(persons)} detection(s)\n"
        section += f"  - Potentially Dangerous Object(s): {len(dangerous_objects)} detection(s)\n"
        section += f"  - Other Object(s): {len(other_objects)} detection(s)\n\n"
        
        # Analyze spatial relationships
        if len(detections) > 1:
            section += "Spatial Relationship Analysis:\n\n"
            
            # Calculate distances between objects
            if persons and dangerous_objects:
                section += "Person-Object Spatial Relationships:\n"
                for p_idx, person in enumerate(persons, 1):
                    p_bbox = person["bbox"]
                    p_center = self._get_bbox_center(p_bbox)
                    
                    section += f"\n  Person #{p_idx} (Center: {p_center[0]:.1f}, {p_center[1]:.1f}):\n"
                    
                    for d_idx, danger_obj in enumerate(dangerous_objects, 1):
                        d_bbox = danger_obj["bbox"]
                        d_center = self._get_bbox_center(d_bbox)
                        distance = self._calculate_distance(p_center, d_center)
                        
                        section += f"    - Distance to {danger_obj['class_name']} #{d_idx}: "
                        section += f"approximately {distance:.1f} pixels\n"
                        
                        # Check for overlap or proximity
                        if self._bboxes_overlap(p_bbox, d_bbox):
                            section += f"      (Bounding boxes overlap - object may be held or "
                            section += f"in close proximity)\n"
                        elif distance < 100:
                            section += f"      (Close proximity detected)\n"
            
            # Object-to-object relationships
            if len(dangerous_objects) > 1:
                section += "\nObject-to-Object Spatial Relationships:\n"
                for i, obj1 in enumerate(dangerous_objects, 1):
                    center1 = self._get_bbox_center(obj1["bbox"])
                    for j, obj2 in enumerate(dangerous_objects[i:], i+1):
                        center2 = self._get_bbox_center(obj2["bbox"])
                        distance = self._calculate_distance(center1, center2)
                        section += f"  - {obj1['class_name']} #{i} to {obj2['class_name']} #{j}: "
                        section += f"approximately {distance:.1f} pixels\n"
        
        # Spatial distribution
        section += "\nSpatial Distribution:\n"
        if len(detections) > 0:
            all_centers = [self._get_bbox_center(d["bbox"]) for d in detections]
            avg_x = sum(c[0] for c in all_centers) / len(all_centers)
            avg_y = sum(c[1] for c in all_centers) / len(all_centers)
            
            section += f"  - Average detection center: ({avg_x:.1f}, {avg_y:.1f}) pixels\n"
            section += f"  - Detections are distributed across the frame\n"
        
        section += "\nLimitations of Spatial Analysis:\n"
        section += "The spatial relationships described above are based on 2D bounding box "
        section += "coordinates and do not account for:\n"
        section += "  - Depth perception or 3D spatial relationships\n"
        section += "  - Camera angle or perspective distortion\n"
        section += "  - Actual physical distances (pixel distances are not equivalent to "
        section += "real-world measurements)\n"
        section += "  - Temporal relationships (this analysis represents a single frame "
        section += "or time point)\n\n"
        
        section += "Expert review is recommended to properly contextualize these spatial "
        section += "observations within the broader scene context.\n"
        
        return section
    
    def _generate_limitations_disclaimer(self) -> str:
        """Generate Limitations & Disclaimer section."""
        section = "=" * 80
        section += "\n6. LIMITATIONS & DISCLAIMER\n"
        section += "=" * 80
        
        section += "\nThis forensic analysis report is generated by an automated artificial "
        section += "intelligence system and is subject to the following limitations and "
        section += "disclaimers:\n\n"
        
        section += "1. AI Analysis Limitations:\n"
        section += "   - Automated detection systems are probabilistic in nature and may "
        section += "produce false positives or false negatives.\n"
        section += "   - Model performance is dependent on training data, environmental "
        section += "conditions, image quality, and scene complexity.\n"
        section += "   - Confidence scores reflect model certainty, not legal standards of "
        section += "proof or expert opinion.\n"
        section += "   - The system may misclassify objects, particularly in cases of "
        section += "occlusion, poor lighting, or unusual viewing angles.\n\n"
        
        section += "2. Expert Review Requirement:\n"
        section += "   - This automated analysis does NOT replace expert human interpretation "
        section += "or professional forensic examination.\n"
        section += "   - All detections, regardless of confidence level, require review by "
        section += "qualified forensic analysts or law enforcement personnel.\n"
        section += "   - The findings presented in this report should be considered as "
        section += "preliminary indicators requiring validation.\n\n"
        
        section += "3. Legal and Evidentiary Considerations:\n"
        section += "   - This report is generated for investigative and analytical purposes "
        section += "only.\n"
        section += "   - The automated system's output should not be considered as "
        section += "definitive evidence without proper chain of custody, expert validation, "
        section += "and legal review.\n"
        section += "   - The use of AI-generated reports in legal proceedings must comply "
        section += "with applicable laws, regulations, and evidentiary standards.\n\n"
        
        section += "4. Technical Limitations:\n"
        section += "   - The analysis is based on visual information only and does not "
        section += "incorporate audio, contextual information, or external data sources.\n"
        section += "   - Temporal analysis is limited to the specific frame(s) or time "
        section += "period(s) analyzed.\n"
        section += "   - The system cannot assess intent, context, or legal implications of "
        section += "detected objects or behaviors.\n\n"
        
        section += "5. Disclaimer of Warranties:\n"
        section += "   - This report is provided \"as is\" without warranties of any kind, "
        section += "express or implied.\n"
        section += "   - The system operators and developers assume no liability for "
        section += "decisions made based on this automated analysis.\n"
        section += "   - Users are responsible for appropriate interpretation and validation "
        section += "of all findings.\n\n"
        
        section += "By using this report, the recipient acknowledges understanding of these "
        section += "limitations and agrees to use the information appropriately and in "
        section += "accordance with applicable professional and legal standards.\n\n"
        
        section += "Report Generated: " + datetime.utcnow().isoformat() + "\n"
        section += "System: Forensic AI Crime Detection System\n"
        section += "Report Type: Automated Forensic Analysis\n"
        
        return section
    
    def _is_dangerous_object(self, class_name: str) -> bool:
        """Check if a class name represents a dangerous object."""
        dangerous_keywords = [
            'gun', 'pistol', 'rifle', 'firearm', 'weapon',
            'knife', 'blade', 'dagger', 'sword', 'machete',
            'scissors', 'hammer', 'axe', 'crowbar', 'bat',
            'bottle', 'bomb', 'explosive'
        ]
        class_lower = class_name.lower()
        return any(keyword in class_lower for keyword in dangerous_keywords)
    
    def _assess_overall_risk(self, detections: List[Dict[str, Any]]) -> str:
        """
        Assess overall risk level based on detections.
        Does NOT modify detection values - only interprets them.
        """
        if not detections:
            return "LOW"
        
        dangerous_count = sum(1 for d in detections if self._is_dangerous_object(d["class_name"]))
        high_conf_dangerous = sum(
            1 for d in detections 
            if self._is_dangerous_object(d["class_name"]) and d["confidence"] >= 0.70
        )
        avg_confidence = sum(d["confidence"] for d in detections) / len(detections)
        
        # Risk assessment logic (interpretation only, no modification)
        if dangerous_count > 0 and high_conf_dangerous > 0 and avg_confidence >= 0.70:
            return "HIGH"
        elif dangerous_count > 0 or avg_confidence >= 0.60:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_bbox_center(self, bbox: List[float]) -> tuple:
        """Calculate center point of bounding box."""
        if len(bbox) < 4:
            return (0.0, 0.0)
        x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def _calculate_distance(self, point1: tuple, point2: tuple) -> float:
        """Calculate Euclidean distance between two points."""
        import math
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def _bboxes_overlap(self, bbox1: List[float], bbox2: List[float]) -> bool:
        """Check if two bounding boxes overlap."""
        if len(bbox1) < 4 or len(bbox2) < 4:
            return False
        
        x1_min, y1_min, x1_max, y1_max = bbox1[0], bbox1[1], bbox1[2], bbox1[3]
        x2_min, y2_min, x2_max, y2_max = bbox2[0], bbox2[1], bbox2[2], bbox2[3]
        
        return not (x1_max < x2_min or x2_max < x1_min or y1_max < y2_min or y2_max < y1_min)
    
    def _generate_error_report(self, error_message: str) -> str:
        """Generate a report when an error occurs."""
        report = "=" * 80
        report += "\nFORENSIC REPORT GENERATION ERROR\n"
        report += "=" * 80
        report += f"\nAn error occurred during report generation: {error_message}\n"
        report += "\nPlease review the detection data format and ensure all required fields "
        report += "are present.\n"
        report += "\nReport Generation Timestamp: " + datetime.utcnow().isoformat() + "\n"
        return report


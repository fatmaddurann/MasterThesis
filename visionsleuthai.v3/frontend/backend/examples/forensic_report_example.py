"""
Example usage of the Forensic Report Generator

This script demonstrates how to use the ForensicReportGenerator
to create professional forensic reports from detection results.
"""

from models.forensic_report_generator import ForensicReportGenerator
from datetime import datetime

def example_usage():
    """Example of generating a forensic report from detection data."""
    
    # Initialize the report generator
    generator = ForensicReportGenerator()
    
    # Example detection data (matches the format from your system)
    detection_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "detections": [
            {
                "label": "knife",
                "confidence": 0.92,
                "bbox": [100.0, 150.0, 200.0, 250.0],
                "risk_level": "High",
                "risk_score": 0.85
            },
            {
                "type": "person",
                "confidence": 0.89,
                "bbox": [300.0, 200.0, 450.0, 600.0],
                "risk_level": "Medium",
                "risk_score": 0.45
            },
            {
                "class_name": "fight",
                "confidence": 0.80,
                "bbox": [50.0, 50.0, 500.0, 400.0],
                "risk_level": "High",
                "risk_score": 0.90
            }
        ]
    }
    
    # Generate the forensic report
    report = generator.generate_report(detection_data)
    
    # Print the report
    print(report)
    
    # You can also save it to a file
    # with open("forensic_report.txt", "w") as f:
    #     f.write(report)
    
    return report


def example_empty_detections():
    """Example with no detections."""
    
    generator = ForensicReportGenerator()
    
    detection_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "detections": []
    }
    
    report = generator.generate_report(detection_data)
    print(report)
    
    return report


def example_low_confidence():
    """Example with low confidence detections."""
    
    generator = ForensicReportGenerator()
    
    detection_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "detections": [
            {
                "class_name": "knife",
                "confidence": 0.35,  # Low confidence
                "bbox": [100.0, 150.0, 200.0, 250.0],
                "risk_level": "Low",
                "risk_score": 0.30
            }
        ]
    }
    
    report = generator.generate_report(detection_data)
    print(report)
    
    return report


if __name__ == "__main__":
    print("=" * 80)
    print("FORENSIC REPORT GENERATOR - EXAMPLE USAGE")
    print("=" * 80)
    print("\nExample 1: Standard detection with multiple objects\n")
    example_usage()
    
    print("\n\n" + "=" * 80)
    print("Example 2: No detections\n")
    example_empty_detections()
    
    print("\n\n" + "=" * 80)
    print("Example 3: Low confidence detection\n")
    example_low_confidence()


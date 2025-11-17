# Forensic Report Generator

## Overview

The `ForensicReportGenerator` is an independent reporting module that generates professional, forensic-standard English reports from detection results. **It does NOT modify any detection values, scores, or thresholds** - it only interprets the results in forensic style.

## Key Features

- ✅ **Non-invasive**: Does not modify detection logic, model parameters, confidence scores, or thresholds
- ✅ **Professional formatting**: Generates formal academic English reports suitable for forensic documentation
- ✅ **Comprehensive sections**: Includes all required forensic report sections
- ✅ **Confidence analysis**: Provides detailed interpretation of confidence scores
- ✅ **Spatial analysis**: Analyzes spatial relationships between detected objects
- ✅ **Legal compliance**: Includes appropriate disclaimers and limitations

## Report Sections

The generated report includes these exact sections:

1. **Executive Summary** - Academic summary of system observations
2. **Forensic Observation Log** - Timestamped description of detections using precise forensic terminology
3. **Behavioral Interpretation & Threat Assessment** - Professional interpretation with risk levels (Low/Medium/High)
4. **Evidential Confidence Analysis** - Detailed analysis of model confidence scores in forensic context
5. **Scene Contextualization** - Spatial relationships among detected objects
6. **Limitations & Disclaimer** - Forensic-compliant caution about AI analysis limitations

## Usage

### Basic Usage

```python
from models.forensic_report_generator import ForensicReportGenerator
from datetime import datetime

# Initialize the generator
generator = ForensicReportGenerator()

# Prepare detection data (matches your system's format)
detection_data = {
    "timestamp": datetime.utcnow().isoformat(),
    "detections": [
        {
            "label": "knife",  # or "type" or "class_name"
            "confidence": 0.92,
            "bbox": [100.0, 150.0, 200.0, 250.0],
            "risk_level": "High",  # optional
            "risk_score": 0.85    # optional
        },
        {
            "type": "person",
            "confidence": 0.89,
            "bbox": [300.0, 200.0, 450.0, 600.0]
        }
    ]
}

# Generate the report
report = generator.generate_report(detection_data)

# Print or save the report
print(report)
# or
with open("forensic_report.txt", "w") as f:
    f.write(report)
```

### Input Format

The generator accepts detection data in the following format:

```python
{
    "timestamp": "ISO format timestamp string",
    "detections": [
        {
            # At least one of: "label", "type", or "class_name"
            "label": "knife",        # or
            "type": "knife",         # or
            "class_name": "knife",   # (all are equivalent)
            
            "confidence": 0.92,      # Required: float 0.0-1.0
            "bbox": [x1, y1, x2, y2],  # Required: bounding box coordinates
            
            # Optional fields (preserved but not required)
            "risk_level": "High",
            "risk_score": 0.85,
            # ... any other fields are preserved
        },
        # ... more detections
    ]
}
```

### Integration with Existing Routes

You can integrate the report generator into your existing API routes without modifying detection logic:

```python
from models.forensic_report_generator import ForensicReportGenerator

report_generator = ForensicReportGenerator()

# In your existing route handler:
results = video_processor.process_frame(frame)  # Your existing detection

# Generate report from results (no modification of detection values)
detection_data = {
    "timestamp": datetime.utcnow().isoformat(),
    "detections": results["detections"]  # Use detections as-is
}

forensic_report = report_generator.generate_report(detection_data)

# Return enhanced results
return {
    **results,  # Original detection data unchanged
    "forensic_report": forensic_report  # Add the report
}
```

## Important Notes

### What This Module Does

- ✅ Takes detection results as input
- ✅ Generates professional forensic reports
- ✅ Interprets confidence scores in forensic context
- ✅ Analyzes spatial relationships
- ✅ Provides risk assessments based on detections

### What This Module Does NOT Do

- ❌ Modify detection values
- ❌ Change confidence scores
- ❌ Adjust thresholds
- ❌ Modify model parameters
- ❌ Change detection logic
- ❌ Filter or remove detections

### Confidence Score Interpretation

The module interprets confidence scores as follows:

- **High Confidence (≥0.80)**: Strong model certainty, but still requires expert review
- **Medium Confidence (0.50-0.79)**: Moderate certainty, expert review recommended
- **Low Confidence (<0.50)**: Weak certainty, marked as "low-confidence observation"

### Risk Assessment

Risk levels are determined based on:
- Presence of dangerous objects
- Confidence scores
- Number of detections

Risk levels: **LOW**, **MEDIUM**, **HIGH**

## Examples

See the `examples/` directory for:
- `forensic_report_example.py` - Basic usage examples
- `integration_example.py` - Integration with existing routes

## Output Format

The report is generated as **plain text** (no HTML) with clear section headers and formatting suitable for:
- Legal documentation
- Forensic case files
- Academic reports
- Professional presentations

## Requirements

- Python 3.7+
- Standard library only (no external dependencies)

## License

Part of the Forensic AI Crime Detection System.


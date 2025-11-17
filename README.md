# Master Thesis - Forensic AI Crime Detection System

## VisionSleuth AI - AI-Powered Forensic Crime Detection

A graduate-level forensic science project that performs crime detection using live camera streams and uploaded video files with AI models (object detection + action recognition).

## Features

- **Live Camera Analysis**: Real-time crime detection from camera feeds
- **Video Upload Analysis**: Comprehensive analysis of uploaded video files
- **Professional Forensic Reports**: Advanced forensic-standard English reports with 6 comprehensive sections
- **Dangerous Object Detection**: Enhanced detection of weapons and dangerous objects
- **Academic Metrics**: Detailed performance metrics and analysis

## Project Structure

```
thesis2/
├── visionsleuthai.v3/
│   ├── frontend/              # Next.js frontend application
│   │   ├── backend/          # FastAPI backend
│   │   │   ├── models/       # AI models and detection logic
│   │   │   ├── routes/       # API routes
│   │   │   └── utils/        # Utility functions
│   │   └── src/              # Frontend source code
│   └── README.md
└── README.md
```

## Key Components

### Backend Models

- **CrimeDetectionModel**: YOLOv8-based object detection
- **ForensicReportGenerator**: Professional forensic report generation
- **VideoProcessor**: Video frame processing and analysis
- **CrimeAnalyzer**: Crime-specific analysis logic

### Frontend Components

- **ForensicAnalysisResults**: Live analysis results display
- **ForensicLiveAnalysisBox**: Real-time analysis interface
- **ComprehensiveAnalysisResults**: Detailed video analysis results

## Installation

### Backend

```bash
cd visionsleuthai.v3/frontend/backend
pip install -r requirements.txt
```

### Frontend

```bash
cd visionsleuthai.v3/frontend
npm install
```

## Usage

### Start Backend

```bash
cd visionsleuthai.v3/frontend/backend
python main.py
```

### Start Frontend

```bash
cd visionsleuthai.v3/frontend
npm run dev
```

## Forensic Report Features

The system generates professional forensic reports with the following sections:

1. **Executive Summary** - Academic summary of system observations
2. **Forensic Observation Log** - Timestamped description of detections
3. **Behavioral Interpretation & Threat Assessment** - Risk level analysis
4. **Evidential Confidence Analysis** - Detailed confidence score interpretation
5. **Scene Contextualization** - Spatial relationship analysis
6. **Limitations & Disclaimer** - Forensic-compliant disclaimers

## Technologies

- **Backend**: Python, FastAPI, YOLOv8, OpenCV
- **Frontend**: Next.js, TypeScript, React, Tailwind CSS
- **AI Models**: YOLOv8x for object detection

## License

This project is part of a Master's Thesis in Forensic Science.

## Author

Fatma Duran - Master's Thesis Project


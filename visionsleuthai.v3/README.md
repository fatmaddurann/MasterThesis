# VisionSleuth AI

A real-time crime behavior detection system using computer vision and machine learning.

## Project Overview

VisionSleuth AI is a comprehensive solution for real-time crime behavior detection through camera feeds and video analysis. The project combines modern web technologies with advanced machine learning capabilities.

### Tech Stack
- Frontend: Next.js (TypeScript)
- Backend: FastAPI (Python)
- ML: YOLOv7
- Cloud: Google Cloud Platform

## Getting Started

### Prerequisites
- Node.js (v18 or higher)
- Python (v3.8 or higher)
- Google Cloud Platform account (for ML features)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vision-sleuth-ai.git
cd vision-sleuth-ai
```

2. Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```

3. Backend Setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

4. Environment Variables:
Create a `.env` file in the backend directory:
```
GCP_PROJECT_ID=your-project-id
GCP_BUCKET_NAME=your-bucket-name
GCP_SERVICE_ACCOUNT_KEY=path/to/service-account-key.json
```

## Project Structure

```
/vision-sleuth-ai
├── /frontend (Next.js)
│   ├── /public
│   ├── /src
│   │   ├── /components
│   │   ├── /pages
│   │   ├── /styles
│   │   ├── /hooks
│   │   └── /utils
├── /backend (Python)
│   ├── main.py
│   ├── /models
│   ├── /routes
│   └── /utils
└── README.md
```

## Features

- Real-time crime behavior detection via camera feed
- Video upload analysis (MP4, MOV formats)
- Modern blue-themed interface with gradient accents
- WebSocket-based real-time communication
- GCP integration for ML model storage and video processing

## Development

### Frontend Development
- TypeScript strict mode enabled
- ESLint with Airbnb config
- TailwindCSS for styling

### Backend Development
- FastAPI with type hints
- Black code formatting
- Pylint score > 8.0 required

## License

MIT License # visionsleuth-ai
# visionsleuthai.v2

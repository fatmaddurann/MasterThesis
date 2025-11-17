# Deployment Guide - VisionSleuth AI

## Deployment Overview

- **Frontend**: Vercel
- **Backend**: Render

## Frontend Deployment (Vercel)

### 1. Vercel Setup

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository: `fatmaddurann/MasterThesis`
4. Set Root Directory: `visionsleuthai.v3/frontend`
5. Framework Preset: Next.js
6. Build Command: `npm run build` (default)
7. Output Directory: `.next` (default)

### 2. Environment Variables (Vercel)

Add these environment variables in Vercel Dashboard → Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://visionsleuth-ai-backend.onrender.com
NEXT_PUBLIC_WS_URL=wss://visionsleuth-ai-backend.onrender.com/ws
```

**Important**: Replace `visionsleuth-ai-backend.onrender.com` with your actual Render backend URL after deployment.

### 3. Vercel Configuration

The `vercel.json` file is already configured with:
- Build settings
- Environment variables
- Routes

## Backend Deployment (Render)

### 1. Render Setup

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `fatmaddurann/MasterThesis`
4. Configure:
   - **Name**: `visionsleuthai-backend`
   - **Root Directory**: `visionsleuthai.v3/frontend/backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`

### 2. Environment Variables (Render)

Add these environment variables in Render Dashboard → Environment:

**Required:**
```
PORT=10000
DEBUG=False
ALLOWED_HOSTS=visionsleuth-ai-backend.onrender.com
```

**Optional (for GCP Storage):**
```
GCP_BUCKET_NAME=your-bucket-name
GCP_SERVICE_ACCOUNT_KEY=base64-encoded-service-account-key
```

**Optional (for model configuration):**
```
MODEL_CONFIDENCE_THRESHOLD=0.35
MODEL_PATH=yolov8x.pt
NMS_IOU_THRESHOLD=0.45
```

### 3. Render Configuration

The `render.yaml` file is already configured in `frontend/backend/render.yaml`.

## Post-Deployment Checklist

### ✅ Backend (Render)

- [ ] Backend is accessible at `https://your-backend.onrender.com`
- [ ] Health check works: `https://your-backend.onrender.com/health`
- [ ] CORS is configured correctly
- [ ] Environment variables are set
- [ ] Model files (yolov8x.pt) are accessible (if needed)

### ✅ Frontend (Vercel)

- [ ] Frontend is accessible at `https://your-frontend.vercel.app`
- [ ] API URL is correctly set to backend URL
- [ ] WebSocket URL is correctly set
- [ ] Environment variables are set
- [ ] Build completes successfully

### ✅ Integration

- [ ] Frontend can connect to backend API
- [ ] WebSocket connections work (for live analysis)
- [ ] Video upload works
- [ ] Live analysis works
- [ ] Forensic reports generate correctly

## Common Issues & Solutions

### Issue: CORS Errors

**Solution**: Update `ALLOWED_HOSTS` in backend to include your Vercel frontend URL:
```
ALLOWED_HOSTS=visionsleuth-ai-backend.onrender.com,visionsleuthai-frontend.vercel.app
```

Also update `origins` in `main.py`:
```python
origins = [
    "https://visionsleuthai-frontend.vercel.app",  # Your Vercel URL
    "https://your-frontend.vercel.app",  # Add your actual URL
    # ... other origins
]
```

### Issue: Model Files Not Found

**Solution**: YOLOv8 models will be downloaded automatically on first run. If you want to pre-download:
1. Models are in `.gitignore` (too large for GitHub)
2. They will be downloaded automatically when the model loads
3. Or upload them to Render's persistent disk

### Issue: Backend Timeout

**Solution**: 
- Render free tier has timeout limits
- For video processing, consider using background jobs
- Increase timeout in Render settings if needed

### Issue: WebSocket Not Working

**Solution**:
- Check WebSocket URL in frontend environment variables
- Ensure Render supports WebSockets (it does)
- Check CORS settings

## Environment Variables Reference

### Backend (Render)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | Yes | 8000 | Server port (Render sets this automatically) |
| `DEBUG` | No | False | Debug mode |
| `ALLOWED_HOSTS` | No | visionsleuth-backend.onrender.com | Allowed hostnames |
| `GCP_BUCKET_NAME` | No | - | GCP Storage bucket name |
| `GCP_SERVICE_ACCOUNT_KEY` | No | - | Base64 encoded GCP service account key |
| `MODEL_CONFIDENCE_THRESHOLD` | No | 0.35 | Detection confidence threshold |
| `MODEL_PATH` | No | yolov8x.pt | YOLOv8 model path |

### Frontend (Vercel)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | - | Backend API URL |
| `NEXT_PUBLIC_WS_URL` | Yes | - | WebSocket URL for live analysis |

## Deployment URLs

After deployment, update these URLs:

1. **Backend URL**: `https://your-backend.onrender.com`
2. **Frontend URL**: `https://your-frontend.vercel.app`

Update in:
- Vercel environment variables (`NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_WS_URL`)
- Backend CORS origins (`main.py`)
- Backend `ALLOWED_HOSTS` environment variable

## Monitoring

### Backend Health Checks

- Health: `GET /health`
- Readiness: `GET /ready`
- Metrics: `GET /metrics`

### Frontend

- Check Vercel deployment logs
- Check browser console for errors
- Test API connectivity

## Support

For deployment issues:
1. Check Render logs: Dashboard → Your Service → Logs
2. Check Vercel logs: Dashboard → Your Project → Deployments → View Logs
3. Check backend health endpoint
4. Verify environment variables are set correctly


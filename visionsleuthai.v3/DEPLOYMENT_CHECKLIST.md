# Deployment Checklist - VisionSleuth AI

## ✅ Pre-Deployment Checklist

### Backend (Render) Hazırlık

- [x] `render.yaml` dosyası backend klasöründe (`frontend/backend/render.yaml`)
- [x] `requirements.txt` dosyası mevcut ve güncel
- [x] `main.py` port ayarları doğru (`$PORT` kullanıyor)
- [x] CORS ayarları yapılandırılmış
- [x] Health check endpoints mevcut (`/health`, `/ready`)

### Frontend (Vercel) Hazırlık

- [x] `vercel.json` dosyası mevcut ve güncel
- [x] `package.json` build script'leri doğru
- [x] `next.config.js` yapılandırılmış
- [x] Environment variables hazır

## 🚀 Deployment Adımları

### 1. Backend Deployment (Render)

1. **Render Dashboard'a Git**
   - https://dashboard.render.com
   - "New +" → "Web Service"

2. **Repository Bağla**
   - GitHub repository: `fatmaddurann/MasterThesis`
   - Branch: `main`

3. **Ayarları Yapılandır**
   ```
   Name: visionsleuthai-backend
   Root Directory: visionsleuthai.v3/frontend/backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
   ```

4. **Environment Variables Ekle**
   ```
   PORT=10000
   DEBUG=False
   ALLOWED_HOSTS=visionsleuth-ai-backend.onrender.com
   ```

5. **Deploy Et**
   - "Create Web Service" tıkla
   - İlk build biraz uzun sürebilir (model indirme)

6. **Backend URL'ini Not Et**
   - Örnek: `https://visionsleuthai-backend-xxxx.onrender.com`
   - Bu URL'yi frontend'de kullanacaksın

### 2. Frontend Deployment (Vercel)

1. **Vercel Dashboard'a Git**
   - https://vercel.com/dashboard
   - "New Project"

2. **Repository Bağla**
   - GitHub repository: `fatmaddurann/MasterThesis`
   - Branch: `main`

3. **Ayarları Yapılandır**
   ```
   Framework Preset: Next.js
   Root Directory: visionsleuthai.v3/frontend
   Build Command: npm run build (otomatik)
   Output Directory: .next (otomatik)
   ```

4. **Environment Variables Ekle**
   ```
   NEXT_PUBLIC_API_URL=https://visionsleuthai-backend-xxxx.onrender.com
   NEXT_PUBLIC_WS_URL=wss://visionsleuthai-backend-xxxx.onrender.com/ws
   ```
   ⚠️ **ÖNEMLİ**: Backend URL'ini Render'dan aldıktan sonra buraya yapıştır!

5. **Deploy Et**
   - "Deploy" tıkla
   - Build tamamlanana kadar bekle

### 3. Post-Deployment Ayarları

#### Backend'de CORS Güncellemesi

Backend deploy edildikten sonra, Vercel frontend URL'ini backend'e ekle:

1. Render Dashboard → Backend Service → Environment
2. `ALLOWED_HOSTS` değişkenini güncelle:
   ```
   ALLOWED_HOSTS=visionsleuth-ai-backend.onrender.com,visionsleuthai-frontend.vercel.app
   ```

3. Backend kodunda (`main.py`) CORS origins'i güncelle:
   ```python
   origins = [
       "https://visionsleuthai-frontend.vercel.app",  # Vercel frontend
       "https://your-actual-vercel-url.vercel.app",  # Gerçek Vercel URL'iniz
       # ... diğerleri
   ]
   ```

4. Backend'i yeniden deploy et (otomatik olabilir)

## 🔍 Test Checklist

### Backend Test

- [ ] Health check: `https://your-backend.onrender.com/health`
- [ ] Ready check: `https://your-backend.onrender.com/ready`
- [ ] API test: `https://your-backend.onrender.com/`
- [ ] CORS headers kontrolü

### Frontend Test

- [ ] Frontend açılıyor: `https://your-frontend.vercel.app`
- [ ] API bağlantısı çalışıyor
- [ ] Video upload testi
- [ ] Live analysis testi
- [ ] Forensic report generation testi

### Integration Test

- [ ] Frontend → Backend API çağrıları çalışıyor
- [ ] WebSocket bağlantısı çalışıyor (live analysis)
- [ ] Video upload ve analiz çalışıyor
- [ ] PDF rapor indirme çalışıyor

## ⚠️ Önemli Notlar

### Model Dosyaları

- YOLOv8 model dosyaları (`.pt`) çok büyük olduğu için GitHub'a push edilmedi
- İlk çalıştırmada model otomatik indirilecek
- Bu işlem biraz zaman alabilir (ilk build'de)

### Render Free Tier Limitleri

- **Timeout**: 30 saniye (video işleme için yeterli olmayabilir)
- **Sleep**: 15 dakika inaktiviteden sonra uyku modu
- **Disk**: Ephemeral (kalıcı değil)

**Çözüm**: Video işleme için background job kullanılıyor, bu yeterli olmalı.

### Vercel Limitleri

- **Build Time**: 45 dakika (yeterli)
- **Function Timeout**: 10 saniye (API routes için)
- **File Size**: 50MB (video upload için yeterli değil, backend'e yönlendiriliyor)

## 🐛 Sorun Giderme

### Backend Başlamıyor

1. Render logs kontrol et
2. `requirements.txt` eksik paket var mı?
3. Port ayarları doğru mu?
4. Environment variables eksik mi?

### Frontend Build Hatası

1. Vercel build logs kontrol et
2. `package.json` dependencies eksik mi?
3. TypeScript hataları var mı?
4. Environment variables set edilmiş mi?

### CORS Hatası

1. Backend'de `ALLOWED_HOSTS` doğru mu?
2. Frontend URL backend CORS origins'de var mı?
3. Backend yeniden deploy edildi mi?

### API Bağlantı Hatası

1. Backend URL doğru mu? (`NEXT_PUBLIC_API_URL`)
2. Backend çalışıyor mu? (`/health` kontrol et)
3. Network tab'de request görünüyor mu?

## 📝 Deployment Sonrası

1. ✅ Backend URL'ini not et
2. ✅ Frontend URL'ini not et
3. ✅ Environment variables'ları güncelle
4. ✅ CORS ayarlarını güncelle
5. ✅ Test et
6. ✅ GitHub'a push et (deployment dosyaları)

## 📞 Destek

Sorun yaşarsanız:
1. Render logs: Dashboard → Service → Logs
2. Vercel logs: Dashboard → Project → Deployments → Logs
3. Browser console: F12 → Console
4. Network tab: F12 → Network


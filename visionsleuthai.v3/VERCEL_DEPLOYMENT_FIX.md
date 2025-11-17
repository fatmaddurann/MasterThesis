# Vercel Deployment Fix

## Sorun
Vercel build hatası: "No Next.js version detected"

## Çözüm

### 1. Vercel.json Sadeleştirildi
Eski format kaldırıldı, sadece environment variables kaldı. Vercel otomatik olarak Next.js'i algılayacak.

### 2. Eksik Dependency Eklendi
`jspdf` package.json'a eklendi (PDF generation için kullanılıyor).

### 3. Vercel Ayarları

**Root Directory**: `visionsleuthai.v3/frontend`

**Framework Preset**: Next.js (otomatik algılanacak)

**Build Command**: Otomatik (`npm run build`)

**Output Directory**: Otomatik (`.next`)

### 4. Environment Variables (Vercel Dashboard'da ayarlayın)

```
NEXT_PUBLIC_API_URL=https://visionsleuth-ai-backend.onrender.com
NEXT_PUBLIC_WS_URL=wss://visionsleuth-ai-backend.onrender.com/ws
```

⚠️ **ÖNEMLİ**: Backend URL'ini Render'dan aldıktan sonra güncelleyin!

## Deployment Adımları

1. **GitHub'a Push**
   ```bash
   git add .
   git commit -m "Fix Vercel deployment configuration"
   git push
   ```

2. **Vercel Dashboard**
   - Project Settings → General
   - Root Directory: `visionsleuthai.v3/frontend` (kontrol et)
   - Framework Preset: Next.js (otomatik)
   - Build Command: Boş bırak (otomatik)
   - Output Directory: Boş bırak (otomatik)

3. **Environment Variables**
   - Settings → Environment Variables
   - Yukarıdaki değişkenleri ekle

4. **Redeploy**
   - Deployments → En son deployment → "Redeploy"

## Test

Build başarılı olmalı ve şu çıktıyı görmelisiniz:
```
✓ Built successfully
```


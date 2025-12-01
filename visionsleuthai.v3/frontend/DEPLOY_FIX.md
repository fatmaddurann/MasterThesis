# 🔧 Live Frame Endpoint Fix - Deploy Talimatları

## ✅ Yapılan Değişiklikler

1. **Backend URL Hardcode Edildi**
   - `src/utils/api.ts` dosyasında `sendFrame` fonksiyonu artık doğrudan Render backend'e istek atıyor
   - URL: `https://masterthesis-zk81.onrender.com/api/live/frame`
   - Debug log eklendi: Console'da `[sendFrame] Calling backend:` mesajını göreceksiniz

2. **Error Handling İyileştirildi**
   - 3 ardışık hatadan sonra interval durduruluyor
   - Daha anlaşılır hata mesajları

## 🚀 Deploy Adımları

### 1. Değişiklikleri Commit ve Push Et

```bash
cd visionsleuthai.v3/frontend
git add .
git commit -m "Fix: Hardcode backend URL for live frame endpoint"
git push origin main
```

### 2. Vercel Otomatik Deploy

- Vercel otomatik olarak deploy edecek
- Deploy tamamlandıktan sonra 2-3 dakika bekle

### 3. Browser Cache Temizle

**ÖNEMLİ:** Production'da test etmeden önce browser cache'i temizle:

1. **Chrome/Edge:**
   - `Ctrl+Shift+R` (Windows) veya `Cmd+Shift+R` (Mac) - Hard refresh
   - Veya DevTools aç → Network tab → "Disable cache" işaretle → Sayfayı yenile

2. **Firefox:**
   - `Ctrl+Shift+R` (Windows) veya `Cmd+Shift+R` (Mac)

### 4. Test Et

1. Live analysis sayfasını aç
2. Browser console'u aç (F12)
3. Şu mesajları görmelisiniz:
   - `[sendFrame] Calling backend: https://masterthesis-zk81.onrender.com/api/live/frame`
4. Network tab'ında isteklerin Render backend'e gittiğini kontrol et
5. Artık 404 hatası olmamalı

## 🔍 Sorun Giderme

### Hala 404 Hatası Alıyorsanız:

1. **Build Cache Sorunu:**
   ```bash
   # Vercel Dashboard'da:
   - Project Settings → General → Clear Build Cache
   - Yeniden deploy et
   ```

2. **Browser Cache:**
   - Incognito/Private mode'da test et
   - Veya farklı browser kullan

3. **Environment Variable Kontrolü:**
   - Vercel Dashboard → Settings → Environment Variables
   - `NEXT_PUBLIC_API_URL` olmasa bile sorun değil (hardcode edildi)

### Hala Vercel Domain'ine İstek Atıyorsa:

1. **Kod Kontrolü:**
   - `src/utils/api.ts` dosyasında `sendFrame` fonksiyonunu kontrol et
   - Line 233'te hardcode URL olmalı: `const backendUrl = 'https://masterthesis-zk81.onrender.com';`

2. **Build Kontrolü:**
   - Local'de build yap: `npm run build`
   - Build output'ta hata var mı kontrol et

## ✅ Beklenen Sonuç

- ✅ Console'da: `[sendFrame] Calling backend: https://masterthesis-zk81.onrender.com/api/live/frame`
- ✅ Network tab'ında: `POST https://masterthesis-zk81.onrender.com/api/live/frame`
- ✅ 404 hatası yok
- ✅ CORS hatası yok (backend CORS zaten yapılandırılmış)
- ✅ Frame'ler başarıyla işleniyor

## 📝 Notlar

- Backend CORS zaten yapılandırılmış (`backend/main.py`)
- Backend URL hardcode edildi (environment variable sorunlarından kaçınmak için)
- Debug log eklendi (production'da console'da görünecek)


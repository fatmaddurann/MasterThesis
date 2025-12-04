# Çözüm Seçenekleri: Live Frame Endpoint

## Mevcut Durum
- Frontend: `https://master-thesis-nu.vercel.app` (Next.js on Vercel)
- Backend: `https://masterthesis-zk81.onrender.com` (FastAPI on Render)
- Sorun: `/api/live/frame` endpoint'i için 404 hatası alınıyor

## 🔹 Seçenek A: Doğrudan Backend Kullanımı + CORS Düzeltmesi

### Avantajları:
- ✅ Daha basit mimari (proxy katmanı yok)
- ✅ Daha az latency (tek hop)
- ✅ Backend CORS zaten yapılandırılmış

### Değişiklikler:

#### 1. Frontend (`src/utils/api.ts`)
```typescript
// DEĞİŞTİR: Relative path yerine doğrudan backend URL kullan
export const sendFrame = async (imageData: string) => {
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://masterthesis-zk81.onrender.com';
  
  const response = await fetch(`${backendUrl}/api/live/frame`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: imageData }),
  });
  // ... rest of the code
};
```

#### 2. Backend CORS (`backend/main.py`)
✅ Zaten yapılandırılmış! `https://master-thesis-nu.vercel.app` origin'i allow list'te.

---

## 🔹 Seçenek B: Next.js Proxy Route (Önerilen)

### Avantajları:
- ✅ CORS sorunu tamamen ortadan kalkar (browser same-origin istek yapar)
- ✅ Backend URL'i frontend'den gizlenir
- ✅ Daha güvenli (backend URL environment variable'da)

### Durum:
✅ Proxy route zaten oluşturulmuş: `src/app/api/live/frame/route.ts`

### Kontrol Edilmesi Gerekenler:
1. ✅ Route dosyası doğru yerde: `src/app/api/live/frame/route.ts`
2. ⚠️ Vercel'de environment variable: `NEXT_PUBLIC_API_URL` ayarlı mı?
3. ⚠️ Route deploy edilmiş mi? (Build output'ta görünüyor mu?)

### Frontend (`src/utils/api.ts`)
✅ Zaten doğru yapılandırılmış - `/api/live/frame` kullanıyor.

---

## 🎯 Öneri: Seçenek B (Proxy Route)

Proxy route zaten hazır ve build'de görünüyor. Sadece Vercel'de deploy edilmesi gerekiyor.

### Hızlı Test:
1. Local'de test et: `npm run dev` → `http://localhost:3000/api/live/frame` POST isteği at
2. Vercel'de environment variable kontrolü yap
3. Deploy sonrası test et

### Alternatif: Seçenek A'ya Geçiş
Eğer proxy route çalışmazsa, Seçenek A'ya geçebiliriz (frontend'i doğrudan backend'e yönlendir).




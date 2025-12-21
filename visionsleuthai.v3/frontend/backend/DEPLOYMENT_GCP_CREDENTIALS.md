# GCP Credentials Deployment Guide

Bu rehber, service account key dosyasını git'e eklemeden production'da (Render/Vercel) GCP bağlantısının nasıl yapılacağını açıklar.

## 🔐 Güvenlik

**Service account key dosyası git'e eklenmemelidir!** Bu dosya hassas bilgiler içerir ve public repository'de olmamalıdır.

## 📋 Çözüm: Environment Variable Kullanımı

Production ortamlarında (Render, Vercel) service account key'i environment variable olarak ekleyin.

## 🚀 Render Deployment

### Adım 1: Service Account Key'i Base64 Encode Et

```bash
# Local'de key dosyasını base64 encode et
cat crime-detection-system-455511-6eb0681355fe.json | base64
```

Veya Python ile:

```python
import base64
import json

with open('crime-detection-system-455511-6eb0681355fe.json', 'r') as f:
    key_data = f.read()
    encoded = base64.b64encode(key_data.encode('utf-8')).decode('utf-8')
    print(encoded)
```

### Adım 2: Render Dashboard'da Environment Variable Ekle

1. **Render Dashboard'a Git**: https://dashboard.render.com
2. **Servisinizi Seçin**: `visionsleuthai-backend`
3. **Environment Tab'ına Git**
4. **Yeni Environment Variable Ekle**:

```
Key: GCP_SERVICE_ACCOUNT_KEY
Value: <base64-encoded-json-string>
```

5. **Bucket Name Ekle**:

```
Key: GCP_BUCKET_NAME
Value: crime-detection-data
```

### Adım 3: Redeploy

Render otomatik olarak redeploy edecek. Veya manuel olarak "Manual Deploy" yapın.

## ☁️ Vercel Deployment (Frontend)

Frontend'de GCP kullanmıyorsanız gerekmez. Eğer kullanıyorsanız:

1. **Vercel Dashboard**: https://vercel.com/dashboard
2. **Project Settings → Environment Variables**
3. **Add Variable**:

```
GCP_SERVICE_ACCOUNT_KEY = <base64-encoded-json-string>
GCP_BUCKET_NAME = crime-detection-data
```

## 💻 Local Development

Local'de key dosyası proje root'unda olduğu sürece otomatik bulunur:

```
/Users/fatma/Desktop/thesis2/crime-detection-system-455511-6eb0681355fe.json
```

Veya environment variable olarak:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/crime-detection-system-455511-6eb0681355fe.json"
export GCP_BUCKET_NAME="crime-detection-data"
```

## 🔧 Kod Nasıl Çalışıyor?

GCP connector şu sırayla credentials arar:

1. **`GCP_SERVICE_ACCOUNT_KEY`** environment variable (base64 veya JSON string) - **Production için**
2. **`GOOGLE_APPLICATION_CREDENTIALS`** environment variable (file path) - **Local için**
3. **Default file path** - Local development için otomatik bulma
4. **Default authentication** - Son çare (genellikle çalışmaz)

## ✅ Test Etme

### Local'de Test

```bash
python visionsleuthai.v3/frontend/backend/scripts/test_gcp_connection.py \
  --bucket "crime-detection-data"
```

### Production'da Test

Render logs'da şu mesajı görmelisiniz:

```
GCPConnector initialized with JSON credentials from environment
GCPConnector initialized with bucket: crime-detection-data
```

## 🐛 Troubleshooting

### "Credentials not found" Hatası

1. **Environment variable kontrol et**: Render dashboard'da `GCP_SERVICE_ACCOUNT_KEY` var mı?
2. **Base64 format kontrol et**: Key doğru encode edilmiş mi?
3. **Bucket name kontrol et**: `GCP_BUCKET_NAME` doğru mu?

### "Permission denied" Hatası

1. **Service account role kontrol et**: Storage Admin veya Storage Object Admin olmalı
2. **Bucket permissions kontrol et**: Service account bucket'a erişebiliyor mu?

### Local'de Çalışmıyor

1. **Key dosyası var mı?**: Proje root'unda kontrol et
2. **Path doğru mu?**: `GOOGLE_APPLICATION_CREDENTIALS` environment variable'ı kontrol et

## 📝 Özet

- ✅ **Local**: Key dosyası otomatik bulunur (git'e eklenmez)
- ✅ **Production**: Environment variable (`GCP_SERVICE_ACCOUNT_KEY`) kullanılır
- ✅ **Güvenlik**: Key dosyası git'e eklenmez, `.gitignore` ile korunur
- ✅ **Esneklik**: Hem file path hem de JSON string desteklenir

Bu yöntemle hem local hem production'da güvenli bir şekilde GCP bağlantısı yapabilirsiniz!

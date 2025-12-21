# GCP Credentials Setup Guide

GCP ile çalışmak için service account key dosyası gerekiyor. Bu rehber, nasıl oluşturacağınızı gösterir.

## 🔑 Adım 1: Service Account Key Oluşturma

### 1.1 Google Cloud Console'da Service Account Oluşturma

1. **Google Cloud Console**'a gidin: https://console.cloud.google.com/
2. **IAM & Admin** → **Service Accounts**'a gidin
3. **+ CREATE SERVICE ACCOUNT** butonuna tıklayın
4. **Service account details**:
   - **Name**: `crime-detection-storage` (veya istediğiniz isim)
   - **Description**: `Service account for crime detection dataset storage`
   - **CREATE AND CONTINUE**'a tıklayın

### 1.2 Role Atama

1. **Grant this service account access to project**:
   - **Role**: `Storage Admin` (veya `Storage Object Admin` - daha kısıtlı)
   - **CONTINUE**'a tıklayın

2. **Grant users access to this service account** (opsiyonel):
   - Şimdilik atlayabilirsiniz
   - **DONE**'a tıklayın

### 1.3 Key Oluşturma

1. Oluşturduğunuz service account'a tıklayın
2. **KEYS** tab'ına gidin
3. **ADD KEY** → **Create new key**'e tıklayın
4. **Key type**: **JSON** seçin
5. **CREATE**'e tıklayın
6. JSON dosyası otomatik indirilecek (örn: `crime-detection-system-455511-xxxxx.json`)

## 📁 Adım 2: Key Dosyasını Yerleştirme

### 2.1 Local Development için

```bash
# Proje root'unda credentials klasörü oluştur
mkdir -p credentials

# İndirilen JSON dosyasını buraya taşı
mv ~/Downloads/crime-detection-system-455511-xxxxx.json credentials/gcp-service-account.json
```

### 2.2 Environment Variable Ayarlama

#### Local (.env dosyası)

`visionsleuthai.v3/frontend/backend/.env` dosyası oluşturun:

```bash
# GCP Configuration
GCP_BUCKET_NAME=crime-detection-data
GOOGLE_APPLICATION_CREDENTIALS=credentials/gcp-service-account.json
```

#### Veya Terminal'de

```bash
export GCP_BUCKET_NAME="crime-detection-data"
export GOOGLE_APPLICATION_CREDENTIALS="/Users/fatma/Desktop/thesis2/visionsleuthai.v3/frontend/backend/credentials/gcp-service-account.json"
```

## 🚀 Adım 3: Render Deployment için

Render'da environment variable olarak eklemeniz gerekiyor:

### 3.1 Key'i Base64 Encode Etme

```bash
# Mac/Linux
base64 -i credentials/gcp-service-account.json

# Veya Python ile
python -c "import base64, json; print(base64.b64encode(open('credentials/gcp-service-account.json', 'rb').read()).decode())"
```

### 3.2 Render Environment Variables

Render Dashboard → Your Service → Environment:

```
GCP_BUCKET_NAME=crime-detection-data
GCP_SERVICE_ACCOUNT_KEY=<base64-encoded-json-content>
```

**Not**: Render'da `GOOGLE_APPLICATION_CREDENTIALS` yerine `GCP_SERVICE_ACCOUNT_KEY` kullanılıyor (base64 encoded).

## ✅ Adım 4: Test Etme

### 4.1 Local Test

```python
from utils.gcp_connector import GCPConnector

# Test connection
try:
    gcp = GCPConnector(bucket_name="crime-detection-data")
    files = gcp.list_files()
    print(f"✅ Connected! Found {len(files)} files")
except Exception as e:
    print(f"❌ Error: {e}")
```

### 4.2 Script Test

```bash
# Dataset script'i test et
python scripts/prepare_gcp_dataset.py \
  --bucket "crime-detection-data" \
  --gcp-path "data/raw" \
  --version "v1"
```

## 🔒 Güvenlik Notları

### ⚠️ ÖNEMLİ: Key Dosyasını Git'e Eklemeyin!

`.gitignore` dosyasına ekleyin:

```bash
# credentials/
credentials/
*.json
!package.json
!package-lock.json
gcp-service-account.json
```

### ✅ Güvenli Alternatifler

1. **Environment Variables**: Key'i environment variable olarak kullanın
2. **Secret Management**: Render'da secret management kullanın
3. **IAM Roles**: Minimum gerekli permission'ları verin (Storage Object Admin)

## 📋 Checklist

- [ ] Service account oluşturuldu
- [ ] Storage Admin role atandı
- [ ] JSON key dosyası indirildi
- [ ] Key dosyası `credentials/` klasörüne taşındı
- [ ] `.env` dosyası oluşturuldu
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` environment variable ayarlandı
- [ ] `.gitignore`'a eklendi (güvenlik)
- [ ] Local test başarılı
- [ ] Render environment variables ayarlandı (deployment için)

## 🐛 Troubleshooting

### "Credentials not found" hatası

```bash
# Environment variable'ı kontrol et
echo $GOOGLE_APPLICATION_CREDENTIALS

# Dosya yolunu kontrol et
ls -la credentials/gcp-service-account.json
```

### "Permission denied" hatası

- Service account'a `Storage Admin` veya `Storage Object Admin` role'ü verildiğinden emin olun
- Bucket permissions'ı kontrol edin

### "Bucket not found" hatası

- Bucket name'in doğru olduğundan emin olun: `crime-detection-data`
- Bucket'ın mevcut olduğunu kontrol edin

## 📞 Yardım

Sorun yaşarsanız:
1. Google Cloud Console'da service account'u kontrol edin
2. IAM permissions'ı kontrol edin
3. Bucket permissions'ı kontrol edin
4. Environment variables'ı kontrol edin

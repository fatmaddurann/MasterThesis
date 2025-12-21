# GCP Credentials Deployment Guide

Bu rehber, service account key dosyasını git'e eklemeden production'da (Render/Vercel) GCP bağlantısının nasıl yapılacağını açıklar.

## 🔐 Güvenlik

**Service account key dosyası git'e eklenmemelidir!** Bu dosya hassas bilgiler içerir ve public repository'de olmamalıdır.

## 📋 Çözüm: Environment Variable Kullanımı

Production ortamlarında (Render, Vercel) service account key'i environment variable olarak ekleyin.

## 🚀 Render Deployment

Render'da iki yöntem var:

### Yöntem 1: Secret Files (Önerilen) ✅

Render'ın Secret Files özelliğini kullanarak dosyayı yükleyin:

1. **Render Dashboard'a Git**: https://dashboard.render.com
2. **Servisinizi Seçin**: `visionsleuthai-backend`
3. **Environment Tab'ına Git**
4. **Secret Files Bölümüne Git**
5. **Secret File Yükle**:
   - File name: `crime-detection-system-455511-6eb0681355fe.json`
   - File content: Service account key JSON içeriğini yapıştırın
6. **Environment Variable Ekle** (opsiyonel, custom path için):
   ```
   Key: GCP_SECRET_FILE_NAME
   Value: crime-detection-system-455511-6eb0681355fe.json
   ```
   Veya custom path için:
   ```
   Key: RENDER_SECRET_FILE_PATH
   Value: /etc/secrets
   ```
7. **Bucket Name Ekle**:
   ```
   Key: GCP_BUCKET_NAME
   Value: crime-detection-data
   ```

**Not**: Secret files genellikle `/etc/secrets/` altında mount edilir. Kod otomatik olarak bu path'leri kontrol eder.

### Yöntem 2: Environment Variable (Alternatif)

Eğer secret files kullanmak istemiyorsanız:

1. **Service Account Key'i Base64 Encode Et**:
```bash
cat crime-detection-system-455511-6eb0681355fe.json | base64
```

2. **Render Dashboard'da Environment Variable Ekle**:
```
Key: GCP_SERVICE_ACCOUNT_KEY
Value: <base64-encoded-json-string>
```

3. **Bucket Name Ekle**:
```
Key: GCP_BUCKET_NAME
Value: crime-detection-data
```

### Adım 3: Redeploy

Render otomatik olarak redeploy edecek. Veya manuel olarak "Manual Deploy" yapın.

## ☁️ Vercel Deployment (Frontend)

Vercel'de secret files özelliği yok, bu yüzden environment variable kullanmanız gerekiyor.

### Adım 1: Service Account Key'i Base64 Encode Et

```bash
# Local'de key dosyasını base64 encode et
cat crime-detection-system-455511-6eb0681355fe.json | base64
```

Veya Python ile:

```python
import base64

with open('crime-detection-system-455511-6eb0681355fe.json', 'r') as f:
    key_data = f.read()
    encoded = base64.b64encode(key_data.encode('utf-8')).decode('utf-8')
    print(encoded)
```

**Önemli**: Çıktıyı kopyalayın, tek satır olmalı (çok uzun olacak).

### Adım 2: Vercel Dashboard'da Environment Variable Ekle

1. **Vercel Dashboard'a Git**: https://vercel.com/dashboard
2. **Projenizi Seçin**: `master-thesis-nu` (veya proje adınız)
3. **Settings → Environment Variables** sekmesine gidin
4. **Add New Variable** butonuna tıklayın

5. **Environment Variable Ekle**:

   **Variable 1:**
   ```
   Name: GCP_SERVICE_ACCOUNT_KEY
   Value: <base64-encoded-json-string> (yukarıdaki çıktıyı yapıştırın)
   Environment: Production, Preview, Development (hepsini seçin)
   ```

   **Variable 2:**
   ```
   Name: GCP_BUCKET_NAME
   Value: crime-detection-data
   Environment: Production, Preview, Development (hepsini seçin)
   ```

6. **Save** butonuna tıklayın

### Adım 3: Redeploy

1. **Deployments** sekmesine gidin
2. **En son deployment'ın yanındaki "..." menüsüne tıklayın**
3. **Redeploy** seçeneğini seçin

Veya otomatik olarak yeni bir commit push ederseniz otomatik deploy olur.

### Notlar

- **Base64 string çok uzun olacak**: Bu normal, tüm JSON içeriği encode edilmiş
- **Environment seçimi**: Production, Preview ve Development için ayrı ayrı ekleyebilirsiniz
- **Güvenlik**: Vercel environment variables şifrelenmiş olarak saklanır
- **Frontend'de kullanım**: Eğer frontend'de GCP kullanmıyorsanız (sadece backend'de kullanılıyorsa), Vercel'de eklemenize gerek yok

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
2. **Render Secret Files** - `/etc/secrets/` veya `RENDER_SECRET_FILE_PATH` - **Render Secret Files için**
3. **`GOOGLE_APPLICATION_CREDENTIALS`** environment variable (file path) - **Custom path için**
4. **Default file path** - Local development için otomatik bulma
5. **Default authentication** - Son çare (genellikle çalışmaz)

### Render Secret Files Path'leri

Kod şu path'leri otomatik kontrol eder:
- `/etc/secrets/crime-detection-system-455511-6eb0681355fe.json` (default)
- `/secrets/crime-detection-system-455511-6eb0681355fe.json` (alternative)
- `RENDER_SECRET_FILE_PATH` environment variable'ındaki path
- `GCP_SECRET_FILE_NAME` environment variable'ındaki dosya adı

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

1. **Secret file kontrol et**: Render dashboard'da secret file yüklü mü?
2. **Secret file path kontrol et**: Render logs'da hangi path'te mount edilmiş?
3. **Environment variable kontrol et**: `GCP_SECRET_FILE_NAME` veya `RENDER_SECRET_FILE_PATH` doğru mu?
4. **Alternatif**: `GCP_SERVICE_ACCOUNT_KEY` environment variable'ı var mı?
5. **Bucket name kontrol et**: `GCP_BUCKET_NAME` doğru mu?

### "Permission denied" Hatası

1. **Service account role kontrol et**: Storage Admin veya Storage Object Admin olmalı
2. **Bucket permissions kontrol et**: Service account bucket'a erişebiliyor mu?

### Local'de Çalışmıyor

1. **Key dosyası var mı?**: Proje root'unda kontrol et
2. **Path doğru mu?**: `GOOGLE_APPLICATION_CREDENTIALS` environment variable'ı kontrol et

## 📝 Özet

### Render (Backend)
- ✅ **Secret Files**: `/etc/secrets/` path'inde otomatik bulunur
- ✅ **Environment Variable**: Alternatif olarak `GCP_SERVICE_ACCOUNT_KEY` kullanılabilir
- ✅ **Bucket Name**: `GCP_BUCKET_NAME` environment variable

### Vercel (Frontend - Eğer GCP kullanıyorsa)
- ✅ **Environment Variable**: `GCP_SERVICE_ACCOUNT_KEY` (base64 encoded JSON string)
- ✅ **Bucket Name**: `GCP_BUCKET_NAME` environment variable
- ⚠️ **Not**: Frontend'de genellikle GCP kullanılmaz, sadece backend'de kullanılır

### Local Development
- ✅ **Key dosyası**: Proje root'unda otomatik bulunur (git'e eklenmez)
- ✅ **Environment Variable**: `GOOGLE_APPLICATION_CREDENTIALS` ile custom path
- ✅ **Güvenlik**: Key dosyası git'e eklenmez, `.gitignore` ile korunur

### Güvenlik
- ✅ Key dosyası git'e eklenmez
- ✅ Production'da environment variables şifrelenmiş olarak saklanır
- ✅ Secret files Render'ın güvenli dosya sistemi üzerinden erişilir

Bu yöntemle hem local hem production'da güvenli bir şekilde GCP bağlantısı yapabilirsiniz!

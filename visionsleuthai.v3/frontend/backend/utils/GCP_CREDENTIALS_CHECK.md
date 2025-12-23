# GCP Credentials Otomatik Algılama Kontrol Listesi

Bu doküman, Render ve Vercel'de GCP credentials'ın otomatik algılanıp algılanmadığını kontrol etmenizi sağlar.

## ✅ Otomatik Algılama Sırası

GCPConnector şu sırayla credentials arar:

### 1. **GCP_SERVICE_ACCOUNT_KEY** (Vercel ve Render için)
- **Vercel**: Environment variable olarak eklenmeli (base64 encoded JSON)
- **Render**: Environment variable olarak eklenebilir (base64 encoded JSON)
- **Öncelik**: En yüksek (hemen kullanılır)

### 2. **Render Secret Files** (Sadece Render)
- **Path'ler**: 
  - `/etc/secrets/crime-detection-system-455511-6eb0681355fe.json` (default)
  - `/secrets/crime-detection-system-455511-6eb0681355fe.json` (alternative)
  - `RENDER_SECRET_FILE_PATH` env var'ındaki path
- **Öncelik**: Yüksek (Render'da önerilen yöntem)

### 3. **GOOGLE_APPLICATION_CREDENTIALS** (Her iki platform)
- **Değer**: Dosya path'i
- **Öncelik**: Orta

### 4. **Default File Path** (Local development)
- **Path'ler**: Proje root'unda otomatik aranır
- **Öncelik**: Düşük (sadece local)

### 5. **Default Authentication** (Son çare)
- **Öncelik**: En düşük (genellikle çalışmaz)

## 🔍 Render Kontrol Listesi

### ✅ Secret Files Yöntemi (Önerilen)

1. **Render Dashboard'da kontrol et**:
   - [ ] Secret Files bölümünde `crime-detection-system-455511-6eb0681355fe.json` var mı?
   - [ ] Environment Variables'da `GCP_BUCKET_NAME` var mı? (Value: `crime-detection-data`)

2. **Render Logs'da kontrol et**:
   ```
   GCP credentials found in Render secret file: /etc/secrets/crime-detection-system-455511-6eb0681355fe.json
   GCPConnector initialized with Render secret file: /etc/secrets/...
   GCPConnector initialized with bucket: crime-detection-data
   GCP bucket connection verified successfully
   ```

### ✅ Environment Variable Yöntemi (Alternatif)

1. **Render Dashboard'da kontrol et**:
   - [ ] `GCP_SERVICE_ACCOUNT_KEY` environment variable var mı? (base64 encoded JSON)
   - [ ] `GCP_BUCKET_NAME` environment variable var mı? (Value: `crime-detection-data`)

2. **Render Logs'da kontrol et**:
   ```
   GCP credentials found in GCP_SERVICE_ACCOUNT_KEY environment variable
   GCPConnector initialized with JSON credentials from GCP_SERVICE_ACCOUNT_KEY environment variable
   GCPConnector initialized with bucket: crime-detection-data
   GCP bucket connection verified successfully
   ```

## 🔍 Vercel Kontrol Listesi

### ✅ Environment Variable Yöntemi (Tek Yöntem)

1. **Vercel Dashboard'da kontrol et**:
   - [ ] `GCP_SERVICE_ACCOUNT_KEY` environment variable var mı? (base64 encoded JSON)
   - [ ] `GCP_BUCKET_NAME` environment variable var mı? (Value: `crime-detection-data`)
   - [ ] **Not**: Vercel'de secret files özelliği yok, sadece environment variables kullanılabilir

2. **Vercel Logs'da kontrol et** (eğer backend Vercel'de çalışıyorsa):
   ```
   GCP credentials found in GCP_SERVICE_ACCOUNT_KEY environment variable
   GCPConnector initialized with JSON credentials from GCP_SERVICE_ACCOUNT_KEY environment variable
   GCPConnector initialized with bucket: crime-detection-data
   GCP bucket connection verified successfully
   ```

## ⚠️ Hata Durumları

### "Credentials not found" Hatası

**Render'da**:
1. Secret file yüklü mü? → Render Dashboard → Environment → Secret Files
2. Secret file path doğru mu? → Logs'da hangi path'ler kontrol ediliyor?
3. Environment variable var mı? → `GCP_SERVICE_ACCOUNT_KEY` veya `GCP_BUCKET_NAME`

**Vercel'de**:
1. Environment variable var mı? → Settings → Environment Variables
2. Base64 encoding doğru mu? → `cat key.json | base64` ile kontrol et
3. JSON formatı doğru mu? → Decode edip JSON.parse() ile test et

### "GCP bucket connection test failed" Uyarısı

Bu uyarı normal olabilir (bucket metadata erişim hatası). Eğer gerçek işlemler çalışıyorsa sorun yok.

### "Failed to initialize GCPConnector" Hatası

1. **Credentials format kontrolü**:
   - Base64 encoded mı? → `echo $GCP_SERVICE_ACCOUNT_KEY | base64 -d | jq .` ile test et
   - JSON formatı geçerli mi? → JSON validator ile kontrol et

2. **Bucket name kontrolü**:
   - `GCP_BUCKET_NAME` environment variable doğru mu?
   - Bucket gerçekten var mı? → GCP Console'dan kontrol et

3. **Permissions kontrolü**:
   - Service account'un Storage Object Admin veya Storage Admin rolü var mı?
   - Bucket'a erişim izni var mı?

## 🧪 Test Komutları

### Local'de Test

```bash
# GCP connection test
python visionsleuthai.v3/frontend/backend/scripts/test_gcp_connection.py \
  --bucket "crime-detection-data"

# Veya environment variable ile
export GCP_SERVICE_ACCOUNT_KEY="<base64-encoded-json>"
export GCP_BUCKET_NAME="crime-detection-data"
python -c "from utils.gcp_connector import GCPConnector; gcp = GCPConnector(); print('Success!')"
```

### Production'da Test

**Render**:
1. Render Dashboard → Logs
2. Backend başlatıldığında şu log'ları ara:
   - `GCPConnector initialized`
   - `GCP bucket connection verified`

**Vercel**:
1. Vercel Dashboard → Logs
2. Backend başlatıldığında şu log'ları ara:
   - `GCPConnector initialized`
   - `GCP bucket connection verified`

## 📝 Özet

| Platform | Yöntem 1 | Yöntem 2 | Otomatik Algılama |
|----------|----------|----------|-------------------|
| **Render** | Secret Files ✅ | Env Var ✅ | ✅ Evet |
| **Vercel** | Env Var ✅ | - | ✅ Evet |
| **Local** | File Path ✅ | Env Var ✅ | ✅ Evet |

**Sonuç**: Her iki platformda da otomatik algılama çalışıyor! ✅

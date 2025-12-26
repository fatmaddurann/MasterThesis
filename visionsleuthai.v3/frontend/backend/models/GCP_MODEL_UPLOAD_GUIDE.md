# GCP'ye Model Yükleme Rehberi

Bu rehber, eğitilmiş model dosyasını GCP Storage'a yüklemek için adım adım talimatlar içerir.

## 📋 Hangi Dosyayı Yüklemelisiniz?

Eğitim sonrası oluşan model dosyaları:
- **`runs/detect/knife_detection_v1/weights/best.pt`** ← **BU DOSYAYI YÜKLEYİN** (en iyi model)
- `runs/detect/knife_detection_v1/weights/last.pt` (son checkpoint, opsiyonel)

## 📍 GCP'de Nereye Yüklemelisiniz?

### Önerilen GCP Path Yapısı:

```
crime-detection-data/
└── models/
    └── trained/
        └── knife_detection_v1/    # veya handgun_knife_v1, vb.
            └── best.pt
```

**Tam GCP Path:** `models/trained/knife_detection_v1/best.pt`

## 🚀 Yükleme Yöntemleri

### Yöntem 1: Otomatik Yükleme (Eğitim Script'i İçinde)

Eğitim script'ini çalıştırırken otomatik yükleme:

```bash
# Environment variable ile otomatik yükleme
export UPLOAD_MODEL_TO_GCP=true
export GCP_BUCKET_NAME="crime-detection-data"

# Model eğit ve otomatik yükle
python models/train.py \
  --use-gcp \
  --gcp-bucket "crime-detection-data" \
  --gcp-dataset-path "data/labeled/v1"
```

Eğitim bittikten sonra model otomatik olarak `models/trained/knife_detection_v1/best.pt` path'ine yüklenecek.

### Yöntem 2: Manuel Yükleme (Python Script)

```python
from utils.gcp_connector import GCPConnector

# GCP connector'ı başlat
gcp = GCPConnector(bucket_name="crime-detection-data")

# Local model dosyası
local_model_path = "runs/detect/knife_detection_v1/weights/best.pt"

# GCP'deki hedef path
gcp_model_path = "models/trained/knife_detection_v1/best.pt"

# Yükle
success = gcp.upload_model(local_model_path, gcp_model_path)

if success:
    print(f"✅ Model başarıyla yüklendi: {gcp_model_path}")
else:
    print("❌ Model yükleme başarısız")
```

### Yöntem 3: Google Cloud Console (Web UI)

1. **Google Cloud Console'a gidin**: https://console.cloud.google.com/storage
2. **Bucket'ı seçin**: `crime-detection-data`
3. **Klasör oluşturun**: `models/trained/knife_detection_v1/`
4. **Dosya yükleyin**: `best.pt` dosyasını bu klasöre sürükleyin

### Yöntem 4: gsutil Komutu (Command Line)

```bash
# gsutil kurulumu (ilk kez kullanıyorsanız)
# https://cloud.google.com/storage/docs/gsutil_install

# Model dosyasını yükle
gsutil cp runs/detect/knife_detection_v1/weights/best.pt \
  gs://crime-detection-data/models/trained/knife_detection_v1/best.pt
```

## ✅ Yükleme Sonrası Kullanım

### Render'da Environment Variable Ayarlama

1. Render Dashboard → Your Service → Environment
2. **Yeni variable ekle:**
   - **Key:** `MODEL_PATH`
   - **Value:** `gcp://crime-detection-data/models/trained/knife_detection_v1/best.pt`
3. **Save** ve **Redeploy**

### Vercel'de Environment Variable Ayarlama

1. Vercel Dashboard → Project → Settings → Environment Variables
2. **Yeni variable ekle:**
   - **Key:** `MODEL_PATH`
   - **Value:** `gcp://crime-detection-data/models/trained/knife_detection_v1/best.pt`
3. **Save** ve **Redeploy**

## 🔍 Yükleme Kontrolü

Model'in başarıyla yüklendiğini kontrol etmek için:

```python
from utils.gcp_connector import GCPConnector

gcp = GCPConnector(bucket_name="crime-detection-data")
exists = gcp.model_exists("models/trained/knife_detection_v1/best.pt")

if exists:
    print("✅ Model GCP'de mevcut")
else:
    print("❌ Model GCP'de bulunamadı")
```

## 📝 Örnek Workflow

### Tam Senaryo:

```bash
# 1. GCP'den dataset indir ve model eğit
python models/train.py \
  --use-gcp \
  --gcp-bucket "crime-detection-data" \
  --gcp-dataset-path "data/labeled/v1"

# 2. Eğitim sonrası model path'i
# runs/detect/knife_detection_v1/weights/best.pt

# 3. Model'i GCP'ye yükle (otomatik veya manuel)
export UPLOAD_MODEL_TO_GCP=true
python models/train.py --use-gcp ...  # Otomatik yükler

# VEYA manuel:
python -c "
from utils.gcp_connector import GCPConnector
gcp = GCPConnector(bucket_name='crime-detection-data')
gcp.upload_model(
    'runs/detect/knife_detection_v1/weights/best.pt',
    'models/trained/knife_detection_v1/best.pt'
)
"

# 4. Render/Vercel'de MODEL_PATH ayarla
# MODEL_PATH=gcp://crime-detection-data/models/trained/knife_detection_v1/best.pt

# 5. Backend'i redeploy et
```

## ⚠️ Önemli Notlar

1. **Model Dosya Boyutu**: Model dosyaları genellikle 10-50MB arasındadır. GCP Storage'da yeterli alan olduğundan emin olun.

2. **Path Formatı**: 
   - ✅ Doğru: `models/trained/knife_detection_v1/best.pt`
   - ❌ Yanlış: `crime-detection-data/models/trained/knife_detection_v1/best.pt` (bucket name path'te olmamalı)

3. **Model Versiyonlama**: Her eğitim için farklı version kullanın:
   - `models/trained/knife_detection_v1/best.pt`
   - `models/trained/knife_detection_v2/best.pt`
   - `models/trained/handgun_knife_v1/best.pt`

4. **Production Model**: Production için özel bir path kullanabilirsiniz:
   - `models/production/current.pt` (symlink veya kopya)

## 🐛 Sorun Giderme

### "Model not found at GCP path" hatası
- GCP path'ini kontrol edin (bucket name path'te olmamalı)
- Model'in gerçekten yüklendiğini Google Cloud Console'dan kontrol edin

### "Permission denied" hatası
- GCP credentials'ın doğru olduğundan emin olun
- Service account'un Storage Admin rolüne sahip olduğunu kontrol edin

### Model yüklendi ama hala default model kullanılıyor
- `MODEL_PATH` environment variable'ını kontrol edin
- Backend'i yeniden deploy edin
- Backend loglarında model path'i kontrol edin

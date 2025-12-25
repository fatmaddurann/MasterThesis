# GCP Model Kullanım Kılavuzu

Bu kılavuz, GCP Storage'da saklanan eğitilmiş modelleri kullanmanızı sağlar.

## 🎯 Hızlı Başlangıç

### 1. Model'i GCP'ye Yükleme

Eğitim sonrası model'i GCP'ye yüklemek için:

```bash
# Environment variable ile otomatik yükleme
export UPLOAD_MODEL_TO_GCP=true
python models/train.py --use-gcp --gcp-bucket "crime-detection-data" --gcp-dataset-path "data/labeled/v1"
```

Veya manuel yükleme:

```python
from utils.gcp_connector import GCPConnector

gcp = GCPConnector(bucket_name="crime-detection-data")
gcp.upload_model(
    local_model_path="runs/detect/knife_detection_v1/weights/best.pt",
    gcp_model_path="models/trained/knife_detection_v1/best.pt"
)
```

### 2. GCP'den Model Kullanma

Render veya Vercel'de environment variable olarak ayarlayın:

```bash
MODEL_PATH=gcp://models/trained/knife_detection_v1/best.pt
```

Sistem otomatik olarak:
- ✅ GCP'den model'i indirir
- ✅ Local cache'e kaydeder (1 gün süreyle)
- ✅ Cache varsa tekrar indirmez
- ✅ GCP'den indirme başarısız olursa default `yolov8n.pt` kullanır

## 📋 GCP Model Path Formatı

```
gcp://bucket-name/path/to/model.pt
```

Örnekler:
- `gcp://crime-detection-data/models/trained/knife_detection_v1/best.pt`
- `gcp://crime-detection-data/models/production/current.pt`

## 🔄 Tam Workflow

### Adım 1: GCP'den Dataset İndir ve Model Eğit

```bash
python models/train.py \
  --use-gcp \
  --gcp-bucket "crime-detection-data" \
  --gcp-dataset-path "data/labeled/v1"
```

### Adım 2: Model'i GCP'ye Yükle

```bash
# Otomatik yükleme (eğitim script'i içinde)
export UPLOAD_MODEL_TO_GCP=true
python models/train.py --use-gcp ...

# Veya manuel yükleme
python -c "
from utils.gcp_connector import GCPConnector
gcp = GCPConnector(bucket_name='crime-detection-data')
gcp.upload_model(
    'runs/detect/knife_detection_v1/weights/best.pt',
    'models/trained/knife_detection_v1/best.pt'
)
"
```

### Adım 3: Render/Vercel'de Model Path Ayarla

**Render:**
- Environment Variables → `MODEL_PATH` → `gcp://crime-detection-data/models/trained/knife_detection_v1/best.pt`

**Vercel:**
- Environment Variables → `MODEL_PATH` → `gcp://crime-detection-data/models/trained/knife_detection_v1/best.pt`

### Adım 4: Backend'i Yeniden Deploy Et

Model otomatik olarak GCP'den indirilecek ve kullanılacak.

## ⚠️ Önemli Notlar

1. **GCP Credentials**: Render'da secret files, Vercel'de environment variables olarak GCP credentials eklemelisiniz.

2. **Model Cache**: Model local cache'e kaydedilir (`models/cached/`). Cache 1 gün geçerli, sonra tekrar indirilir.

3. **Fallback**: GCP'den model indirme başarısız olursa, sistem otomatik olarak default `yolov8n.pt` kullanır.

4. **Class Auto-Detection**: Eğitim script'i artık GCP dataset'inden class'ları otomatik algılar (handgun, knife, dinner_knife, vb.)

## 🐛 Sorun Giderme

### "Model not found at GCP path" hatası
- GCP bucket adını ve model path'ini kontrol edin
- Model'in GCP'ye yüklendiğinden emin olun

### "GCP_BUCKET_NAME not set" hatası
- Render/Vercel'de `GCP_BUCKET_NAME` environment variable'ını ekleyin

### Model hala eski sonuçları veriyor
- Cache'i temizleyin: `rm -rf models/cached/`
- Backend'i yeniden başlatın

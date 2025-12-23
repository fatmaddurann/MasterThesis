# GCP Storage Dataset ile Model Eğitimi Kılavuzu

Bu kılavuz, GCP Storage'a eklediğiniz görselleri kullanarak model eğitimi yapmanızı sağlar.

## 🎯 Hızlı Başlangıç

### 1. GCP'den Dataset İndirip Model Eğitme

```bash
# GCP'den dataset indir ve model eğit
python models/train.py --use-gcp --gcp-bucket "crime-detection-data" --gcp-dataset-path "data/labeled/v1"
```

Bu komut:
- ✅ GCP Storage'dan `data/labeled/v1` path'indeki dataset'i indirir
- ✅ Local'e `data/` klasörüne kaydeder
- ✅ `data.yaml` dosyasını kullanır (GCP'den indirilen)
- ✅ Model eğitimini başlatır

### 2. Sadece Local Dataset ile Eğitim

```bash
# Local dataset kullan (GCP kullanma)
python models/train.py
```

## 📋 Detaylı Kullanım

### GCP Dataset Yapısı

GCP Storage'da dataset şu yapıda olmalı:

```
crime-detection-data/
└── data/
    └── labeled/
        └── v1/                    # Dataset version
            ├── train/
            │   ├── images/       # Training images
            │   └── labels/       # YOLO format labels (.txt)
            ├── val/
            │   ├── images/       # Validation images
            │   └── labels/       # YOLO format labels (.txt)
            └── data.yaml         # YOLO dataset config
```

### Komut Satırı Parametreleri

```bash
python models/train.py \
  --use-gcp \                                    # GCP'den dataset indir
  --gcp-bucket "crime-detection-data" \          # GCP bucket adı
  --gcp-dataset-path "data/labeled/v1" \        # GCP'deki dataset path'i
  --local-dataset-path "data"                    # Local'e indirilecek path
```

### Environment Variables

```bash
# GCP credentials için
export GCP_BUCKET_NAME="crime-detection-data"
export GCP_SERVICE_ACCOUNT_KEY="<json_key>"  # Veya secret file kullan

# Model path için (eğitim sonrası)
export MODEL_PATH="runs/detect/knife_detection_v1/weights/best.pt"
```

## 🔄 Tam Workflow

### Adım 1: GCP'ye Görselleri Ekle
- GCP Console'dan `crime-detection-data/data/raw/knife/` ve `handgun/` klasörlerine görseller ekle
- Negative examples için `data/raw/negative/toothbrush/` ve `baseball_bat/` ekle

### Adım 2: Dataset Hazırlama (İlk Kez)

```bash
# GCP'den raw görselleri indir, YOLO formatına dönüştür
python scripts/prepare_gcp_dataset.py \
  --bucket "crime-detection-data" \
  --gcp-path "data/raw" \
  --version "v1" \
  --include-negative
```

### Adım 3: Labeling (LabelImg ile)

```bash
# LabelImg kurulumu
pip install labelImg
labelImg

# LabelImg'de:
# - Open Dir: data/labeled/v1/train/images/
# - Change Save Dir: data/labeled/v1/train/labels/
# - Format: YOLO
# - Classes: knife (0), handgun (1)
```

### Adım 4: Label'ları GCP'ye Yükle

```bash
# Label'ları GCP'ye yükle
python scripts/prepare_gcp_dataset.py \
  --bucket "crime-detection-data" \
  --gcp-path "data/raw" \
  --version "v1" \
  --include-negative
```

### Adım 5: Model Eğitimi (GCP'den Dataset İndirerek)

```bash
# GCP'den dataset indir ve model eğit
python models/train.py \
  --use-gcp \
  --gcp-bucket "crime-detection-data" \
  --gcp-dataset-path "data/labeled/v1" \
  --device cuda  # GPU varsa, yoksa cpu
```

### Adım 6: Eğitilmiş Model'i Kullan

```bash
# Environment variable olarak ayarla
export MODEL_PATH="runs/detect/knife_detection_v1/weights/best.pt"

# Veya Render/Vercel'de environment variable olarak ekle
# MODEL_PATH=runs/detect/knife_detection_v1/weights/best.pt
```

## ⚠️ Önemli Notlar

1. **İlk Eğitim**: İlk kez eğitim yapıyorsanız, `prepare_gcp_dataset.py` script'ini çalıştırıp dataset'i YOLO formatına dönüştürmelisiniz.

2. **Labeling Zorunlu**: GCP'ye eklediğiniz görseller için **mutlaka labeling yapmalısınız**. Labeling olmadan model eğitilemez.

3. **Model Path**: Eğitim sonrası `MODEL_PATH` environment variable'ını güncellemeyi unutmayın, aksi halde sistem hala pretrained `yolov8n.pt` kullanır.

4. **GCP Credentials**: Render'da secret files, Vercel'de environment variables olarak GCP credentials eklemelisiniz.

## 🐛 Sorun Giderme

### "No files found at GCP path" hatası
- GCP bucket adını ve path'i kontrol edin
- GCP credentials'ın doğru olduğundan emin olun

### "data.yaml not found" hatası
- `prepare_gcp_dataset.py` script'ini çalıştırıp dataset'i hazırlayın
- GCP'de `data/labeled/v1/data.yaml` dosyasının olduğundan emin olun

### Model hala eski sonuçları veriyor
- `MODEL_PATH` environment variable'ını güncelleyin
- Backend'i yeniden başlatın

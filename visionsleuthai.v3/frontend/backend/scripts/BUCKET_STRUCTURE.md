# Google Cloud Storage Bucket Yapısı - crime-detection-data

Bu doküman, `crime-detection-data` bucket'ı için önerilen dosya düzenini açıklar.

## 📁 Önerilen Klasör Yapısı

```
crime-detection-data/
│
├── data/                          # Dataset'ler
│   ├── raw/                       # Ham görüntüler (label'lanmamış)
│   │   ├── knife/
│   │   │   ├── images/
│   │   │   │   ├── knife_001.jpg
│   │   │   │   ├── knife_002.jpg
│   │   │   │   └── ...
│   │   │   └── metadata.json      # URL'ler, kaynaklar, vb.
│   │   ├── gun/
│   │   │   ├── images/
│   │   │   └── metadata.json
│   │   ├── negative/              # Yanlış pozitif örnekler
│   │   │   ├── toothbrush/
│   │   │   ├── scissors/
│   │   │   └── baseball_bat/
│   │   └── external/              # Harici kaynaklardan (Roboflow, Kaggle)
│   │       ├── roboflow/
│   │       └── kaggle/
│   │
│   ├── labeled/                    # Label'lanmış dataset'ler
│   │   ├── v1/                     # Dataset versiyonu
│   │   │   ├── train/
│   │   │   │   ├── images/
│   │   │   │   │   ├── knife_001.jpg
│   │   │   │   │   └── ...
│   │   │   │   └── labels/
│   │   │   │       ├── knife_001.txt
│   │   │   │       └── ...
│   │   │   ├── val/
│   │   │   │   ├── images/
│   │   │   │   └── labels/
│   │   │   ├── test/               # (Opsiyonel) Test seti
│   │   │   │   ├── images/
│   │   │   │   └── labels/
│   │   │   ├── data.yaml           # YOLO config dosyası
│   │   │   └── dataset_info.json   # Dataset metadata
│   │   │
│   │   └── v2/                     # Yeni versiyon (daha fazla data)
│   │       └── ...
│   │
│   └── processed/                  # İşlenmiş/ön işlenmiş görüntüler
│       ├── augmented/               # Data augmentation sonuçları
│       └── normalized/              # Normalize edilmiş görüntüler
│
├── models/                         # ML Modelleri
│   ├── pretrained/                 # Pretrained modeller
│   │   ├── yolov8n.pt
│   │   ├── yolov8s.pt
│   │   └── yolov8m.pt
│   │
│   ├── trained/                    # Eğitilmiş modeller
│   │   ├── knife_detection/
│   │   │   ├── v1/                 # Model versiyonu
│   │   │   │   ├── best.pt         # En iyi model
│   │   │   │   ├── last.pt         # Son checkpoint
│   │   │   │   ├── config.yaml     # Training config
│   │   │   │   └── metrics.json    # Training metrics
│   │   │   │
│   │   │   ├── v2/                 # Yeni versiyon
│   │   │   │   └── ...
│   │   │   │
│   │   │   └── production/         # Production'da kullanılan model
│   │   │       └── current.pt -> v2/best.pt  # Symlink veya kopya
│   │   │
│   │   └── weapon_detection/
│   │       └── ...
│   │
│   └── experiments/                 # Deneme modelleri
│       ├── exp_001/
│       └── exp_002/
│
├── training/                        # Training artifacts
│   ├── runs/                       # Training run'ları
│   │   ├── 2024-12-20_knife_v1/
│   │   │   ├── weights/
│   │   │   │   ├── best.pt
│   │   │   │   └── last.pt
│   │   │   ├── results.png
│   │   │   ├── confusion_matrix.png
│   │   │   └── training_log.json
│   │   │
│   │   └── 2024-12-21_knife_v2/
│   │       └── ...
│   │
│   ├── logs/                       # Training log'ları
│   │   ├── train_2024-12-20.log
│   │   └── ...
│   │
│   └── checkpoints/                # Intermediate checkpoints
│       └── ...
│
├── videos/                         # Video dosyaları (mevcut)
│   ├── uploads/                    # Kullanıcı yüklemeleri
│   │   └── 2024/12/20/
│   │       └── video_001.mp4
│   │
│   ├── test/                       # Test videoları
│   │   └── ...
│   │
│   └── samples/                    # Örnek videolar (demo için)
│       └── ...
│
├── results/                        # Analiz sonuçları
│   ├── video_analysis/
│   │   ├── {video_id}/
│   │   │   ├── analysis.json
│   │   │   ├── frames/
│   │   │   │   └── frame_001.jpg
│   │   │   └── report.pdf
│   │   └── ...
│   │
│   └── live_analysis/
│       └── {session_id}/
│           └── ...
│
├── temp/                           # Geçici dosyalar (mevcut)
│   ├── uploads/                    # Upload sırasında geçici
│   ├── processing/                 # İşleme sırasında
│   └── cache/                      # Cache dosyaları
│
└── config/                         # Konfigürasyon dosyaları
    ├── dataset_configs/
    │   ├── knife_detection_v1.yaml
    │   └── ...
    │
    └── model_configs/
        ├── training_config.yaml
        └── inference_config.yaml
```

## 📋 Klasör Açıklamaları

### `/data/` - Dataset'ler

#### `/data/raw/`
- **Amaç**: İnternetten toplanan ham görüntüler
- **İçerik**: Label'lanmamış görüntüler, metadata
- **Kullanım**: Dataset collection script'i buraya yükler

#### `/data/labeled/`
- **Amaç**: Label'lanmış, eğitime hazır dataset'ler
- **Yapı**: YOLO formatında (images/ + labels/)
- **Versiyonlama**: v1, v2, v3 (her yeni dataset versiyonu)

#### `/data/processed/`
- **Amaç**: İşlenmiş görüntüler (augmentation, normalization)
- **Kullanım**: Training öncesi preprocessing sonuçları

### `/models/` - Modeller

#### `/models/pretrained/`
- **Amaç**: Ultralytics'ten indirilen pretrained modeller
- **İçerik**: yolov8n.pt, yolov8s.pt, vb.

#### `/models/trained/`
- **Amaç**: Kendi eğittiğiniz modeller
- **Versiyonlama**: Her model versiyonu ayrı klasörde
- **Production**: `production/current.pt` → aktif model

#### `/models/experiments/`
- **Amaç**: Deneme modelleri (hyperparameter tuning, vb.)

### `/training/` - Training Artifacts

- **Runs**: Her training run'ı ayrı klasörde
- **Logs**: Training log dosyaları
- **Checkpoints**: Intermediate model checkpoints

### `/videos/` - Video Dosyaları (Mevcut)

- **uploads/**: Kullanıcı yüklemeleri (tarih bazlı)
- **test/**: Test videoları
- **samples/**: Demo videoları

### `/results/` - Analiz Sonuçları

- **video_analysis/**: Video analiz sonuçları
- **live_analysis/**: Canlı analiz sonuçları

### `/temp/` - Geçici Dosyalar (Mevcut)

- Upload, processing, cache için

## 🚀 Kullanım Senaryoları

### Senaryo 1: Dataset Toplama

```python
from scripts.collect_dataset import DatasetCollector

collector = DatasetCollector(bucket_name="crime-detection-data")

# Görüntüleri topla
knife_urls = [...]  # URL listesi
collector.collect_from_urls(
    knife_urls, 
    category="knife"
)
# → data/raw/knife/images/ altına yüklenir
```

### Senaryo 2: Labeling Sonrası Organize Etme

```bash
# Labeling yaptıktan sonra:
# data/labeled/v1/train/ ve data/labeled/v1/val/ klasörlerine taşı
```

### Senaryo 3: Model Eğitimi

```python
from models.train import train_yolov8

# data.yaml'ı GCP'den indir veya local'de oluştur
train_yolov8(
    data_yaml="data/labeled/v1/data.yaml",
    name="knife_detection_v1"
)
# → training/runs/ altına kaydedilir
```

### Senaryo 4: Production Model Deployment

```python
# En iyi modeli production'a kopyala
from utils.gcp_connector import GCPConnector

gcp = GCPConnector(bucket_name="crime-detection-data")

# Best model'i production'a kopyala
gcp.upload_file(
    "training/runs/2024-12-20_knife_v1/weights/best.pt",
    "models/trained/knife_detection/production/current.pt"
)
```

## 📝 Environment Variables

```bash
# .env veya environment variables
GCP_BUCKET_NAME=crime-detection-data
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# Model paths
MODEL_PATH=models/trained/knife_detection/production/current.pt
DATASET_PATH=data/labeled/v1
```

## 🔄 Versiyonlama Stratejisi

### Dataset Versiyonlama
- `v1`: İlk dataset (500-1000 görüntü)
- `v2`: Genişletilmiş dataset (2000+ görüntü)
- `v3`: Daha fazla çeşitlilik

### Model Versiyonlama
- `v1`: İlk eğitilmiş model
- `v2`: Daha iyi hyperparameters
- `v3`: Daha fazla data ile eğitilmiş

## ✅ Best Practices

1. **Versiyonlama**: Her dataset ve model versiyonunu ayrı klasörde tut
2. **Metadata**: Her dataset için `dataset_info.json` ekle
3. **Backup**: Önemli modelleri yedekle
4. **Lifecycle Policies**: Eski temp dosyaları otomatik sil
5. **Permissions**: Production modelleri read-only yap

## 🔧 GCP Lifecycle Policy Örneği

```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 30,
          "matchesPrefix": ["temp/"]
        }
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {
          "age": 90,
          "matchesPrefix": ["training/runs/"]
        }
      }
    ]
  }
}
```

Bu policy:
- `temp/` altındaki dosyaları 30 gün sonra siler
- `training/runs/` altındaki eski run'ları 90 gün sonra NEARLINE'a taşır (daha ucuz)

## 📊 Örnek Dataset Info JSON

```json
{
  "version": "v1",
  "created_at": "2024-12-20T10:00:00Z",
  "total_images": 1500,
  "train_images": 1200,
  "val_images": 300,
  "classes": ["knife", "gun", "scissors", "baseball_bat", "person"],
  "source": "Roboflow + Manual collection",
  "labeling_tool": "LabelImg",
  "notes": "First dataset for knife detection"
}
```

Bu yapı ile:
- ✅ Organize dataset yönetimi
- ✅ Model versiyonlama
- ✅ Training history takibi
- ✅ Production deployment kolaylığı
- ✅ Ölçeklenebilirlik


# Training Workflow - GCP Dataset ile Model Eğitimi

Bu rehber, GCP'deki dataset'inizi kullanarak model eğitimi için adım adım talimatlar içerir.

## 📁 Mevcut GCP Yapısı

```
crime-detection-data/
└── data/
    └── raw/
        ├── knife/              # 200 görsel ✅
        ├── handgun/            # 200 görsel ✅
        └── negative/
            ├── toothbrush/     # Ekleyeceksiniz
            └── baseball_bat/    # Ekleyeceksiniz
```

## 🚀 Adım 1: Dataset Hazırlama

### 1.1 GCP'den Dataset İndirme ve YOLO Formatına Dönüştürme

```bash
# Dataset'i GCP'den indir, train/val split yap, YOLO formatına dönüştür
python scripts/prepare_gcp_dataset.py \
  --bucket "crime-detection-data" \
  --gcp-path "data/raw" \
  --version "v1" \
  --train-ratio 0.8 \
  --include-negative
```

Bu script:
- ✅ GCP'den raw görüntüleri indirir
- ✅ Train/val split yapar (80/20)
- ✅ YOLO formatına dönüştürür (images/ + labels/)
- ✅ Negative examples için boş label dosyaları oluşturur
- ✅ `data.yaml` oluşturur
- ✅ Hazır dataset'i GCP'ye yükler: `data/labeled/v1/`

### 1.2 Çıktı Yapısı

```
data/labeled/v1/
├── train/
│   ├── images/
│   │   ├── knife_001.jpg
│   │   ├── handgun_001.jpg
│   │   └── ...
│   └── labels/
│       ├── knife_001.txt      # (Labeling yapmanız gerekiyor)
│       ├── handgun_001.txt     # (Labeling yapmanız gerekiyor)
│       └── ...
├── val/
│   ├── images/
│   └── labels/
└── data.yaml
```

## 🏷️ Adım 2: Labeling (En Önemli Adım!)

### 2.1 LabelImg ile Labeling

```bash
# LabelImg kurulumu
pip install labelImg

# LabelImg'i çalıştır
labelImg
```

**Labeling Adımları:**

1. **Open Dir**: `data/labeled/v1/train/images/` klasörünü aç
2. **Change Save Dir**: `data/labeled/v1/train/labels/` klasörünü seç
3. **Format**: YOLO formatını seç (sağ üst köşe)
4. **Classes**: 
   - `knife` → Class ID: 0
   - `handgun` → Class ID: 1
5. **Labeling**: Her görüntüde bıçak/handgun çevresine bounding box çiz
6. **Save**: Her görüntü için label dosyası otomatik kaydedilir

### 2.2 Label Formatı

Her görüntü için `.txt` dosyası (örn: `knife_001.txt`):

```
0 0.5 0.5 0.3 0.4
```

- `0`: Class ID (knife=0, handgun=1)
- `0.5 0.5`: Bounding box merkezi (normalize, 0-1)
- `0.3 0.4`: Genişlik ve yükseklik (normalize, 0-1)

### 2.3 Negative Examples

Negative examples (toothbrush, baseball_bat) için:
- **Boş label dosyaları** zaten oluşturuldu
- Bu görüntüler training sırasında **background** olarak kullanılacak
- Model bu nesneleri **bıçak/handgun olarak algılamayı öğrenmeyecek**

## 📊 Adım 3: Dataset'i GCP'ye Yükleme

Labeling tamamlandıktan sonra:

```bash
# Label'ları GCP'ye yükle
python scripts/prepare_gcp_dataset.py \
  --bucket "crime-detection-data" \
  --gcp-path "data/raw" \
  --version "v1" \
  --include-negative
```

Bu, güncellenmiş label dosyalarını GCP'ye yükler.

## 🎯 Adım 4: Model Eğitimi

### 4.1 GCP'den Dataset İndirme (Training için)

```python
from scripts.prepare_gcp_dataset import GCPDatasetPreparer

preparer = GCPDatasetPreparer(bucket_name="crime-detection-data")

# Dataset'i local'e indir
preparer.download_from_gcp(
    "data/labeled/v1",
    "local_dataset"
)
```

### 4.2 Training Başlatma

```python
from models.train import train_yolov8, create_data_yaml

# data.yaml'ı kontrol et (GCP'den indirilen)
data_yaml = "local_dataset/data.yaml"

# Model eğit
train_yolov8(
    model_size='s',      # 's'=small (daha iyi doğruluk)
    epochs=200,
    batch_size=32,      # GPU varsa 32, CPU için 8-16
    img_size=640,
    data_yaml=data_yaml,
    device='cuda',      # 'cuda' if GPU, 'cpu' otherwise
    name='knife_handgun_v1',
    patience=50
)
```

### 4.3 Training Sonuçları

Training sonrası:
- **Best model**: `runs/detect/knife_handgun_v1/weights/best.pt`
- **Last model**: `runs/detect/knife_handgun_v1/weights/last.pt`
- **Metrics**: `runs/detect/knife_handgun_v1/results.png`

## 📤 Adım 5: Model'i GCP'ye Yükleme

```python
from utils.gcp_connector import GCPConnector

gcp = GCPConnector(bucket_name="crime-detection-data")

# Best model'i GCP'ye yükle
gcp.upload_file(
    "runs/detect/knife_handgun_v1/weights/best.pt",
    "models/trained/knife_handgun_detection/v1/best.pt"
)

# Production'a kopyala
gcp.upload_file(
    "runs/detect/knife_handgun_v1/weights/best.pt",
    "models/trained/knife_handgun_detection/production/current.pt"
)
```

## 🔧 Adım 6: Model'i Kullanma

### 6.1 Environment Variable

```bash
# Render environment variables
MODEL_PATH=models/trained/knife_handgun_detection/production/current.pt
```

### 6.2 Kod Güncellemesi

Model zaten `handgun` class'ını destekliyor (güncellendi). Sadece model path'ini ayarlayın.

## ✅ Checklist

- [ ] GCP'de raw görüntüler hazır (knife, handgun, negative)
- [ ] `prepare_gcp_dataset.py` çalıştırıldı
- [ ] Dataset YOLO formatına dönüştürüldü
- [ ] Labeling yapıldı (LabelImg ile)
- [ ] Label'lar GCP'ye yüklendi
- [ ] Model eğitildi
- [ ] Best model GCP'ye yüklendi
- [ ] Production model path ayarlandı

## 🎯 Beklenen Sonuçlar

### Öncesi (COCO Model)
- ❌ Bıçak → `toothbrush`, `scissors`, `baseball_bat` olarak algılanıyor
- ❌ Handgun → Doğru algılanmıyor

### Sonrası (Custom Model)
- ✅ Bıçak → `knife` olarak doğru algılanıyor
- ✅ Handgun → `handgun` olarak doğru algılanıyor
- ✅ Toothbrush → Bıçak olarak algılanmıyor (negative example)
- ✅ Baseball bat → Bıçak olarak algılanmıyor (negative example)

## 💡 İpuçları

1. **Labeling Kalitesi**: Bounding box'lar tam olmalı, nesneyi tamamen kapsamalı
2. **Çeşitlilik**: Farklı açılar, ışıklandırma, arka planlar
3. **Negative Examples**: En az 100-200 negative example (toothbrush, baseball_bat)
4. **Validation Set**: Validation set'te de çeşitlilik olmalı
5. **Iterative Training**: İlk model sonuçlarına göre daha fazla data ekleyin

## 🔗 Yararlı Komutlar

```bash
# Dataset hazırlama
python scripts/prepare_gcp_dataset.py --bucket "crime-detection-data" --include-negative

# Model eğitimi
python models/train.py

# Model validation
python -c "from models.train import validate_model; validate_model('runs/detect/knife_handgun_v1/weights/best.pt', 'local_dataset/data.yaml')"
```

Bu workflow ile GCP'deki dataset'inizi kullanarak custom model eğitebilir ve yanlış pozitifleri önemli ölçüde azaltabilirsiniz!

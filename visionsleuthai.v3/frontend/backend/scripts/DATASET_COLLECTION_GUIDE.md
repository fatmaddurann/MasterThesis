# Dataset Collection Guide - Bıçak ve Silah Tespiti

Bu rehber, internetten bıçak ve silah fotoğrafları toplayıp Google Cloud Storage'a yüklemek için adım adım talimatlar içerir.

## ✅ Neden Google Cloud Storage?

1. **Ölçeklenebilirlik**: Binlerce görüntüyü saklayabilirsiniz
2. **Erişilebilirlik**: Her yerden erişim
3. **Organizasyon**: Klasör yapısı ile düzenli saklama
4. **Mevcut Altyapı**: Zaten GCP connector'ınız var

## 📋 Adım 1: GCP Bucket Hazırlama

### 1.1 Google Cloud Console'da Bucket Oluşturma

```bash
# Google Cloud Console → Storage → Create Bucket
# Bucket name: vision-sleuth-dataset (veya istediğiniz isim)
# Location: us-central1 (veya size yakın)
# Storage class: Standard
```

### 1.2 Service Account Key Oluşturma

```bash
# Google Cloud Console → IAM & Admin → Service Accounts
# Create Service Account → Dataset Uploader
# Role: Storage Admin
# Create Key → JSON → İndir
```

### 1.3 Environment Variable Ayarlama

```bash
# Local'de
export GCP_BUCKET_NAME="vision-sleuth-dataset"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Veya .env dosyasına ekleyin
GCP_BUCKET_NAME=vision-sleuth-dataset
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

## 📥 Adım 2: Görüntü Kaynakları

### 2.1 Ücretsiz Dataset Kaynakları

#### Roboflow (Önerilen)
- **URL**: https://roboflow.com/datasets
- **Arama**: "knife detection", "weapon detection"
- **Avantaj**: Zaten YOLO formatında label'lar var
- **Kullanım**:
```python
from scripts.collect_dataset import DatasetCollector

collector = DatasetCollector()
collector.download_from_roboflow("workspace/dataset-name/1")
```

#### Kaggle
- **URL**: https://www.kaggle.com/datasets
- **Arama**: "knife detection", "weapon dataset"
- **Örnekler**:
  - Knife Detection Dataset
  - Weapon Detection Dataset
  - Security Camera Dataset

#### Open Images Dataset
- **URL**: https://storage.googleapis.com/openimages/web/index.html
- **Filtreleme**: "knife", "gun", "weapon" class'ları
- **Not**: Label'ları manuel düzenlemeniz gerekebilir

#### Google Images (Manuel)
- Google Images'da "knife", "gun" araması yapın
- Yüksek kaliteli görüntüleri seçin
- **Önemli**: Telif haklarına dikkat edin!

### 2.2 Manuel URL Listesi Oluşturma

`urls.json` dosyası oluşturun:

```json
[
  {
    "url": "https://example.com/knife1.jpg",
    "label": "knife"
  },
  {
    "url": "https://example.com/knife2.jpg",
    "label": "knife"
  },
  {
    "url": "https://example.com/gun1.jpg",
    "label": "gun"
  }
]
```

## 🚀 Adım 3: Görüntüleri Toplama

### 3.1 Script Kullanımı

```bash
# Roboflow'dan indir
python scripts/collect_dataset.py \
  --roboflow "workspace/knife-detection/1" \
  --bucket "vision-sleuth-dataset"

# URL listesinden indir
python scripts/collect_dataset.py \
  --urls-file urls.json \
  --category knife \
  --bucket "vision-sleuth-dataset"
```

### 3.2 Manuel Toplama

```python
from scripts.collect_dataset import DatasetCollector

collector = DatasetCollector(bucket_name="vision-sleuth-dataset")

# Bıçak görüntüleri
knife_urls = [
    "https://example.com/knife1.jpg",
    "https://example.com/knife2.jpg",
    # ... daha fazla URL
]

collector.collect_from_urls(knife_urls, category="knife")

# Silah görüntüleri
gun_urls = [
    "https://example.com/gun1.jpg",
    # ... daha fazla URL
]

collector.collect_from_urls(gun_urls, category="gun")
```

## 🏷️ Adım 4: Labeling (En Önemli Adım!)

### 4.1 Neden Labeling Gerekli?

YOLO formatında her görüntü için bounding box annotation'ları gerekli:
```
class_id center_x center_y width height
```

### 4.2 Labeling Tool'ları

#### LabelImg (Önerilen - Ücretsiz)
```bash
# Install
pip install labelImg

# Run
labelImg
```

**Kullanım**:
1. Open Dir → Görüntü klasörünü seç
2. Change Save Dir → Label klasörünü seç
3. YOLO formatını seç (sağ üst)
4. Her görüntüde bıçak/silah çevresine bounding box çiz
5. Class name: `knife`, `gun`, vb.

#### Roboflow (Ücretli ama kolay)
- Roboflow'da dataset oluştur
- Web UI'da labeling yap
- YOLO formatında export et

#### CVAT (Açık kaynak, güçlü)
- Web-based labeling tool
- Çoklu kullanıcı desteği
- https://cvat.org/

### 4.3 Label Formatı

Her görüntü için `.txt` dosyası (aynı isim):

**knife_001.jpg** → **knife_001.txt**
```
0 0.5 0.5 0.3 0.4
```

- `0`: Class ID (knife=0, gun=1, vb.)
- `0.5 0.5`: Bounding box merkezi (normalize, 0-1)
- `0.3 0.4`: Genişlik ve yükseklik (normalize, 0-1)

### 4.4 Class Mapping

`data.yaml` dosyasında class isimleri:
```yaml
names:
  - knife
  - gun
  - scissors
  - baseball_bat
  - person
```

## 📊 Adım 5: Dataset Organizasyonu

### 5.1 GCP'de Klasör Yapısı

```
datasets/
├── knife/
│   ├── images/
│   │   ├── knife_001.jpg
│   │   ├── knife_002.jpg
│   │   └── ...
│   ├── labels/
│   │   ├── knife_001.txt
│   │   ├── knife_002.txt
│   │   └── ...
│   └── metadata.json
├── gun/
│   ├── images/
│   └── labels/
└── yolo/
    ├── train/
    │   ├── images/
    │   └── labels/
    └── val/
        ├── images/
        └── labels/
```

### 5.2 Train/Val Split

```python
# 80% train, 20% validation
from sklearn.model_selection import train_test_split

images = list(Path("data/images").glob("*.jpg"))
train_images, val_images = train_test_split(images, test_size=0.2, random_state=42)

# Move to train/val folders
# (script eklenebilir)
```

## ✅ Adım 6: Dataset Kalitesi Kontrolü

### 6.1 Minimum Gereksinimler

- **Bıçak görüntüleri**: En az 500-1000 görüntü
- **Silah görüntüleri**: En az 500-1000 görüntü
- **Çeşitlilik**: 
  - Farklı açılar
  - Farklı ışıklandırma
  - Farklı bıçak/silah tipleri
  - Farklı arka planlar

### 6.2 Negative Examples (Önemli!)

Yanlış pozitifleri azaltmak için:
- `toothbrush` görüntüleri (bıçak değil!)
- `scissors` görüntüleri (bıçak değil!)
- `baseball_bat` görüntüleri (bıçak değil!)

Bu görüntüleri **NEGATIVE** olarak label'layın veya ayrı bir klasöre koyun.

## 🎯 Önerilen Dataset Boyutları

| Kategori | Minimum | Önerilen | İdeal |
|----------|---------|----------|-------|
| Knife | 500 | 1000 | 2000+ |
| Gun | 500 | 1000 | 2000+ |
| Negative (toothbrush, etc.) | 200 | 500 | 1000+ |

## 📝 Checklist

- [ ] GCP bucket oluşturuldu
- [ ] Service account key ayarlandı
- [ ] Görüntü kaynakları belirlendi
- [ ] Görüntüler toplandı (minimum 500 per category)
- [ ] Labeling yapıldı (YOLO formatında)
- [ ] Train/val split yapıldı (80/20)
- [ ] Negative examples eklendi
- [ ] Dataset GCP'ye yüklendi
- [ ] `data.yaml` oluşturuldu

## 🚀 Sonraki Adım: Training

Dataset hazır olduğunda:

```python
from models.train import train_yolov8, create_data_yaml

# data.yaml oluştur
create_data_yaml(
    train_images="data/train/images",
    val_images="data/val/images",
    output_path="data.yaml"
)

# Model eğit
train_yolov8(
    model_size='s',
    epochs=200,
    batch_size=32,
    data_yaml='data.yaml',
    device='cuda'  # GPU varsa
)
```

## 💡 İpuçları

1. **Çeşitlilik**: Farklı açılar, ışıklandırma, arka planlar
2. **Kalite**: Yüksek çözünürlüklü görüntüler (min 640x640)
3. **Labeling Doğruluğu**: Bounding box'lar tam olmalı
4. **Negative Examples**: Yanlış pozitifleri azaltmak için önemli
5. **Validation Set**: Overfitting'i önlemek için ayrı validation set

## 🔗 Yararlı Linkler

- **Roboflow**: https://roboflow.com/datasets
- **Kaggle**: https://www.kaggle.com/datasets
- **LabelImg**: https://github.com/heartexlabs/labelImg
- **YOLOv8 Docs**: https://docs.ultralytics.com/

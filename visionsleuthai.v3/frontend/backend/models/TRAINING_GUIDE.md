# YOLOv8 Training Guide for Knife Detection

Bu rehber, bıçak tespiti için YOLOv8 modelini nasıl eğiteceğinizi açıklar.

## Sorun

Mevcut YOLOv8 COCO modeli bıçakları doğru tespit edemiyor ve şu yanlış pozitifleri üretiyor:
- `toothbrush` (diş fırçası)
- `scissors` (makas)
- `baseball_bat` (beyzbol sopası)

## Çözüm

1. **Custom Dataset Oluşturma**: Bıçak görüntüleri içeren özel bir dataset
2. **YOLOv8 Fine-tuning**: COCO pretrained model üzerinde fine-tuning
3. **False Positive Filtreleme**: Kod seviyesinde yanlış pozitif filtreleme (zaten eklendi)

## Dataset Hazırlama

### 1. Klasör Yapısı

```
data/
├── train/
│   ├── images/
│   │   ├── knife_001.jpg
│   │   ├── knife_002.jpg
│   │   └── ...
│   └── labels/
│       ├── knife_001.txt
│       ├── knife_002.txt
│       └── ...
├── val/
│   ├── images/
│   │   ├── knife_101.jpg
│   │   └── ...
│   └── labels/
│       ├── knife_101.txt
│       └── ...
└── data.yaml
```

### 2. Label Format (YOLO)

Her görüntü için bir `.txt` dosyası (aynı isim):
```
class_id center_x center_y width height
```

Örnek (`knife_001.txt`):
```
0 0.5 0.5 0.3 0.4
```
- `0`: Bıçak sınıfı (class_id)
- `0.5 0.5`: Bounding box merkezi (normalize edilmiş, 0-1 arası)
- `0.3 0.4`: Genişlik ve yükseklik (normalize edilmiş)

### 3. Dataset Kaynakları

Bıçak görüntüleri için:
- **Roboflow**: [Knife Detection Dataset](https://roboflow.com/datasets)
- **Kaggle**: Knife detection datasets
- **Open Images Dataset**: Filter for knife images
- **Kendi görüntüleriniz**: Çeşitli açılardan, ışıklandırmalarda bıçak fotoğrafları

**Önemli**: Dataset'te çeşitlilik olmalı:
- Farklı bıçak tipleri (mutfak bıçağı, çakı, bıçak, vb.)
- Farklı açılar ve pozisyonlar
- Farklı ışıklandırma koşulları
- Yanlış pozitif örnekler (toothbrush, scissors, baseball bat) - bunları NEGATIVE olarak işaretleyin

## Training

### 1. data.yaml Oluşturma

```python
from models.train import create_data_yaml

create_data_yaml(
    train_images="data/train/images",
    val_images="data/val/images",
    output_path="data.yaml",
    classes=['knife', 'gun', 'scissors', 'baseball_bat', 'bottle', 'hammer', 'person']
)
```

### 2. Model Eğitimi

```python
from models.train import train_yolov8

# Hızlı test için küçük model
results = train_yolov8(
    model_size='n',      # 'n'=nano (hızlı), 's'=small, 'm'=medium
    epochs=100,
    batch_size=16,
    img_size=640,
    data_yaml='data.yaml',
    device='cpu',        # 'cuda' if GPU available
    name='knife_detection_v1'
)
```

### 3. GPU Kullanımı (Önerilen)

```python
# CUDA kullanılabilirse
import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'

results = train_yolov8(
    model_size='s',      # GPU varsa 's' veya 'm' kullanın
    epochs=200,
    batch_size=32,       # GPU'da daha büyük batch size
    device=device,
    name='knife_detection_v1'
)
```

## Model Kullanımı

Eğitilmiş modeli kullanmak için:

1. **Model dosyasını kaydedin**: `runs/detect/knife_detection_v1/weights/best.pt`

2. **Environment variable ayarlayın**:
```bash
export MODEL_PATH=runs/detect/knife_detection_v1/weights/best.pt
```

3. **Veya kodda**:
```python
model = CrimeDetectionModel(mode="live_analysis")
model.model_path = "runs/detect/knife_detection_v1/weights/best.pt"
model.load_model()
```

## Performans İyileştirme

### 1. Hız Optimizasyonu (Zaten eklendi)

- **Half Precision (FP16)**: GPU'da 2x hız artışı
- **Model Warmup**: İlk inference gecikmesini azaltır
- **Frame Resizing**: Büyük görüntüleri küçültme
- **Max Detections**: Maksimum tespit sayısını sınırlama

### 2. Doğruluk İyileştirme

- **False Positive Filtreleme**: Aspect ratio ve confidence-based filtering (zaten eklendi)
- **Context-aware Mapping**: Görsel özelliklere göre daha iyi sınıflandırma (zaten eklendi)
- **Custom Training**: Bıçak için özel eğitim (bu rehber)

## Önerilen Training Parametreleri

### Hızlı Test (CPU)
```python
model_size='n'
epochs=50
batch_size=8
img_size=640
```

### Production (GPU)
```python
model_size='s'  # veya 'm' daha iyi doğruluk için
epochs=200
batch_size=32
img_size=640
```

## Validation

Eğitim sonrası modeli validate edin:

```python
from models.train import validate_model

metrics = validate_model(
    model_path="runs/detect/knife_detection_v1/weights/best.pt",
    data_yaml="data.yaml",
    img_size=640,
    conf_threshold=0.25,
    iou_threshold=0.45
)

print(f"mAP50: {metrics.box.map50}")
print(f"mAP50-95: {metrics.box.map}")
```

## Troubleshooting

### 1. "CUDA out of memory"
- Batch size'ı azaltın: `batch_size=16` → `batch_size=8`
- Model boyutunu küçültün: `model_size='m'` → `model_size='s'`

### 2. "No labels found"
- Label dosyalarının doğru formatta olduğundan emin olun
- `data.yaml` içindeki path'lerin doğru olduğunu kontrol edin

### 3. "Low mAP"
- Daha fazla veri ekleyin
- Data augmentation ayarlarını artırın
- Epoch sayısını artırın

## Sonuç

Eğitilmiş model, bıçak tespitinde daha yüksek doğruluk sağlayacak ve yanlış pozitifleri (toothbrush, scissors, baseball bat) filtreleyecektir. Mevcut kod zaten false positive filtreleme içeriyor, bu yüzden custom training ile birlikte çok daha iyi sonuçlar alacaksınız.

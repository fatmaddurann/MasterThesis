"""
YOLOv8 Custom Training Script for Dangerous Object Detection
Specifically optimized for knife detection to reduce false positives
"""
import os
from pathlib import Path
from ultralytics import YOLO
import yaml
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_data_yaml(
    train_images: str,
    val_images: str,
    output_path: str = "data.yaml",
    classes: list = None
):
    """
    Create YOLOv8 data.yaml configuration file.
    
    Args:
        train_images: Path to training images directory
        val_images: Path to validation images directory
        output_path: Output path for data.yaml
        classes: List of class names (default: dangerous objects)
    """
    if classes is None:
        classes = [
            'knife',           # Primary focus: reduce false positives
            'gun',
            'scissors',
            'baseball_bat',
            'bottle',
            'hammer',
            'person'           # Keep person for context
        ]
    
    data_config = {
        'path': str(Path(train_images).parent.absolute()),
        'train': 'train/images',
        'val': 'val/images',
        'nc': len(classes),
        'names': classes
    }
    
    with open(output_path, 'w') as f:
        yaml.dump(data_config, f, default_flow_style=False)
    
    logger.info(f"Created data.yaml at {output_path}")
    logger.info(f"Classes: {classes}")
    return output_path


def train_yolov8(
    model_size: str = 'n',  # n, s, m, l, x
    epochs: int = 100,
    batch_size: int = 16,
    img_size: int = 640,
    data_yaml: str = 'data.yaml',
    pretrained: bool = True,
    device: str = 'cpu',
    project: str = 'runs/detect',
    name: str = 'knife_detection',
    patience: int = 50,
    save_period: int = 10
):
    """
    Train YOLOv8 model for dangerous object detection.
    
    Args:
        model_size: Model size ('n'=nano, 's'=small, 'm'=medium, 'l'=large, 'x'=xlarge)
        epochs: Number of training epochs
        batch_size: Batch size for training
        img_size: Input image size
        data_yaml: Path to data.yaml configuration
        pretrained: Use pretrained COCO weights
        device: Device to use ('cpu', 'cuda', '0', '1', etc.)
        project: Project directory for outputs
        name: Experiment name
        patience: Early stopping patience
        save_period: Save checkpoint every N epochs
    """
    # Load pretrained YOLOv8 model
    model_name = f'yolov8{model_size}.pt'
    logger.info(f"Loading pretrained model: {model_name}")
    
    if pretrained:
        model = YOLO(model_name)
    else:
        # Train from scratch (not recommended)
        model = YOLO(f'yolov8{model_size}.yaml')
    
    # Verify data.yaml exists
    if not os.path.exists(data_yaml):
        raise FileNotFoundError(f"data.yaml not found at {data_yaml}. Create it first using create_data_yaml()")
    
    logger.info(f"Starting training with config: {data_yaml}")
    logger.info(f"Training parameters: epochs={epochs}, batch={batch_size}, img_size={img_size}")
    
    # Train the model
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        device=device,
        project=project,
        name=name,
        patience=patience,
        save_period=save_period,
        # Augmentation settings for better knife detection
        hsv_h=0.015,      # Hue augmentation
        hsv_s=0.7,        # Saturation augmentation
        hsv_v=0.4,        # Value augmentation
        degrees=10,       # Rotation augmentation
        translate=0.1,    # Translation augmentation
        scale=0.5,        # Scale augmentation
        shear=2,          # Shear augmentation
        perspective=0.0,  # Perspective augmentation
        flipud=0.0,        # Vertical flip (usually 0 for weapons)
        fliplr=0.5,       # Horizontal flip
        mosaic=1.0,       # Mosaic augmentation
        mixup=0.1,        # Mixup augmentation
        copy_paste=0.0,    # Copy-paste augmentation
        # Optimization settings
        optimizer='AdamW',
        lr0=0.01,         # Initial learning rate
        lrf=0.01,         # Final learning rate (lr0 * lrf)
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        # Loss weights (focus on classification for knife detection)
        box=7.5,          # Box loss gain
        cls=0.5,          # Class loss gain (lower for better precision)
        dfl=1.5,          # DFL loss gain
        # Validation settings
        val=True,
        plots=True,
        # Other settings
        verbose=True,
        seed=42,
        deterministic=True,
        single_cls=False,
        rect=False,
        cos_lr=False,
        close_mosaic=10,
        resume=False,
        amp=True,         # Automatic Mixed Precision for speed
        fraction=1.0,
        profile=False,
        freeze=None,
        # Multi-scale training
        multi_scale=False,
    )
    
    logger.info("Training completed!")
    logger.info(f"Best model saved at: {results.save_dir}/weights/best.pt")
    logger.info(f"Last model saved at: {results.save_dir}/weights/last.pt")
    
    return results


def validate_model(
    model_path: str,
    data_yaml: str,
    img_size: int = 640,
    conf_threshold: float = 0.25,
    iou_threshold: float = 0.45
):
    """
    Validate trained model on validation set.
    
    Args:
        model_path: Path to trained model weights
        data_yaml: Path to data.yaml configuration
        img_size: Input image size
        conf_threshold: Confidence threshold
        iou_threshold: IoU threshold for NMS
    """
    logger.info(f"Loading model from {model_path}")
    model = YOLO(model_path)
    
    logger.info("Running validation...")
    metrics = model.val(
        data=data_yaml,
        imgsz=img_size,
        conf=conf_threshold,
        iou=iou_threshold,
        plots=True,
        save_json=True
    )
    
    logger.info("Validation completed!")
    logger.info(f"mAP50: {metrics.box.map50}")
    logger.info(f"mAP50-95: {metrics.box.map}")
    
    return metrics


def main():
    """
    Main training script.
    Adjust paths and parameters as needed.
    """
    # Dataset paths (adjust these to your dataset structure)
    base_dir = Path("data")
    train_images = base_dir / "train" / "images"
    val_images = base_dir / "val" / "images"
    
    # Create data.yaml if it doesn't exist
    data_yaml = "data.yaml"
    if not os.path.exists(data_yaml):
        logger.info("Creating data.yaml...")
        create_data_yaml(
            train_images=str(train_images),
            val_images=str(val_images),
            output_path=data_yaml
        )
    
    # Training parameters
    model_size = 'n'  # Use 'n' for speed, 's' or 'm' for better accuracy
    epochs = 100
    batch_size = 16
    img_size = 640
    device = 'cpu'  # Change to 'cuda' or '0' if GPU available
    
    # Train model
    logger.info("=" * 50)
    logger.info("Starting YOLOv8 Training for Knife Detection")
    logger.info("=" * 50)
    
    results = train_yolov8(
        model_size=model_size,
        epochs=epochs,
        batch_size=batch_size,
        img_size=img_size,
        data_yaml=data_yaml,
        device=device,
        name='knife_detection_v1'
    )
    
    # Validate best model
    best_model_path = Path(results.save_dir) / "weights" / "best.pt"
    if best_model_path.exists():
        logger.info("=" * 50)
        logger.info("Validating Best Model")
        logger.info("=" * 50)
        validate_model(
            model_path=str(best_model_path),
            data_yaml=data_yaml,
            img_size=img_size
        )
    
    logger.info("=" * 50)
    logger.info("Training Pipeline Completed!")
    logger.info("=" * 50)
    logger.info(f"Best model: {best_model_path}")
    logger.info(f"To use the trained model, set MODEL_PATH={best_model_path}")


if __name__ == '__main__':
    main()

"""
YOLOv8 Custom Training Script for Dangerous Object Detection
Specifically optimized for knife detection to reduce false positives
Supports both local dataset and GCP Storage dataset
"""
import os
import sys
from pathlib import Path
from ultralytics import YOLO
import yaml
import logging
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def detect_classes_from_labels(train_images: str, val_images: str) -> list:
    """
    Auto-detect class names from YOLO label files.
    Reads all .txt files in train/labels and val/labels directories,
    extracts unique class IDs, and maps them to class names based on
    GCP dataset structure (handgun, knife, dinner_knife, etc.)
    
    Args:
        train_images: Path to training images directory
        val_images: Path to validation images directory
    
    Returns:
        List of class names sorted alphabetically
    """
    try:
        # Get label directories
        train_labels = str(Path(train_images).parent / "labels")
        val_labels = str(Path(val_images).parent / "labels")
        
        # Collect all class IDs from label files
        class_ids = set()
        
        # Check train labels
        if os.path.exists(train_labels):
            label_files = glob.glob(os.path.join(train_labels, "*.txt"))
            for label_file in label_files:
                try:
                    with open(label_file, 'r') as f:
                        for line in f:
                            parts = line.strip().split()
                            if parts:
                                class_id = int(parts[0])
                                class_ids.add(class_id)
                except Exception as e:
                    logger.debug(f"Error reading label file {label_file}: {str(e)}")
        
        # Check val labels
        if os.path.exists(val_labels):
            label_files = glob.glob(os.path.join(val_labels, "*.txt"))
            for label_file in label_files:
                try:
                    with open(label_file, 'r') as f:
                        for line in f:
                            parts = line.strip().split()
                            if parts:
                                class_id = int(parts[0])
                                class_ids.add(class_id)
                except Exception as e:
                    logger.debug(f"Error reading label file {label_file}: {str(e)}")
        
        if not class_ids:
            logger.warning("No class IDs found in label files")
            return []
        
        # Map class IDs to names based on GCP dataset structure
        # Common class mappings (can be extended)
        class_mapping = {
            0: 'handgun',
            1: 'knife',
            2: 'dinner_knife',
            3: 'person',
            4: 'scissors',
            5: 'baseball_bat',
            6: 'toothbrush',  # negative example
        }
        
        # Build class list based on detected IDs
        detected_classes = []
        for class_id in sorted(class_ids):
            if class_id in class_mapping:
                detected_classes.append(class_mapping[class_id])
            else:
                # Unknown class ID, use generic name
                detected_classes.append(f"class_{class_id}")
        
        # Always include 'person' if not already present (common in crime detection)
        if 'person' not in detected_classes:
            detected_classes.append('person')
        
        logger.info(f"Auto-detected classes from labels: {detected_classes}")
        return sorted(detected_classes)
        
    except Exception as e:
        logger.error(f"Error auto-detecting classes: {str(e)}")
        return []


def create_data_yaml(
    train_images: str,
    val_images: str,
    output_path: str = "data.yaml",
    classes: list = None,
    auto_detect_classes: bool = True
):
    """
    Create YOLOv8 data.yaml configuration file.
    
    Args:
        train_images: Path to training images directory
        val_images: Path to validation images directory
        output_path: Output path for data.yaml
        classes: List of class names (default: dangerous objects)
        auto_detect_classes: If True, automatically detect classes from label files
    """
    if classes is None:
        if auto_detect_classes:
            # Auto-detect classes from label files
            classes = detect_classes_from_labels(train_images, val_images)
            if not classes:
                # Fallback to default classes
                logger.warning("Could not auto-detect classes, using defaults")
                classes = [
                    'knife',
                    'handgun',
                    'person'
                ]
        else:
            # Updated classes based on GCP dataset structure
            classes = [
                'knife',
                'handgun',
                'person'
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
    Supports both local dataset and GCP dataset.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Train YOLOv8 model for dangerous object detection')
    parser.add_argument('--use-gcp', action='store_true', 
                       help='Download dataset from GCP Storage before training')
    parser.add_argument('--gcp-bucket', type=str, default=None,
                       help='GCP bucket name (default: from GCP_BUCKET_NAME env var)')
    parser.add_argument('--gcp-dataset-path', type=str, default='data/labeled/v1',
                       help='GCP path to labeled dataset (default: data/labeled/v1)')
    parser.add_argument('--local-dataset-path', type=str, default='data',
                       help='Local dataset path (default: data)')
    args = parser.parse_args()
    
    # If use-gcp flag is set, download dataset from GCP
    if args.use_gcp:
        logger.info("=" * 50)
        logger.info("Downloading dataset from GCP Storage...")
        logger.info("=" * 50)
        
        try:
            # Import GCP dataset preparer
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from scripts.prepare_gcp_dataset import GCPDatasetPreparer
            
            bucket_name = args.gcp_bucket or os.getenv('GCP_BUCKET_NAME', 'crime-detection-data')
            preparer = GCPDatasetPreparer(bucket_name=bucket_name)
            
            # Download labeled dataset from GCP
            local_dataset_path = args.local_dataset_path
            gcp_dataset_path = args.gcp_dataset_path
            
            logger.info(f"Downloading from GCP: {gcp_dataset_path} -> {local_dataset_path}")
            preparer.download_from_gcp(gcp_dataset_path, local_dataset_path)
            
            # Update paths to use downloaded dataset
            base_dir = Path(local_dataset_path)
            train_images = base_dir / "train" / "images"
            val_images = base_dir / "val" / "images"
            data_yaml = base_dir / "data.yaml"
            
            if not data_yaml.exists():
                logger.warning(f"data.yaml not found at {data_yaml}. Creating from dataset structure...")
                create_data_yaml(
                    train_images=str(train_images),
                    val_images=str(val_images),
                    output_path=str(data_yaml),
                    auto_detect_classes=True  # Auto-detect classes from GCP dataset
                )
            else:
                logger.info(f"Using data.yaml from GCP: {data_yaml}")
            
            data_yaml = str(data_yaml)
            
        except Exception as e:
            logger.error(f"Failed to download dataset from GCP: {str(e)}")
            logger.error("Falling back to local dataset...")
            args.use_gcp = False
    
    # If not using GCP or GCP download failed, use local dataset
    if not args.use_gcp:
        base_dir = Path(args.local_dataset_path)
        train_images = base_dir / "train" / "images"
        val_images = base_dir / "val" / "images"
        
        # Create data.yaml if it doesn't exist
        data_yaml = "data.yaml"
        if not os.path.exists(data_yaml):
            logger.info("Creating data.yaml...")
            create_data_yaml(
                train_images=str(train_images),
                val_images=str(val_images),
                output_path=data_yaml,
                auto_detect_classes=True  # Auto-detect classes from labels
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
    
    # Automatically upload model to GCP (if GCP is available)
    # This makes it easier - model is automatically available after training
    if best_model_path.exists():
        try:
            from utils.gcp_connector import GCPConnector
            bucket_name = os.getenv("GCP_BUCKET_NAME", "crime-detection-data")
            
            # Try to initialize GCP connector
            try:
                gcp = GCPConnector(bucket_name=bucket_name)
                
                # Generate GCP path from experiment name
                exp_name = Path(best_model_path).parent.parent.name  # e.g., "knife_detection_v1"
                gcp_model_path = f"models/trained/{exp_name}/{Path(best_model_path).name}"
                
                logger.info("=" * 60)
                logger.info("Uploading model to GCP Storage...")
                logger.info(f"  Local: {best_model_path}")
                logger.info(f"  GCP:   {bucket_name}/{gcp_model_path}")
                
                if gcp.upload_model(str(best_model_path), gcp_model_path):
                    logger.info("=" * 60)
                    logger.info("✅ Model successfully uploaded to GCP!")
                    logger.info("=" * 60)
                    logger.info(f"GCP Path: {gcp_model_path}")
                    logger.info("")
                    logger.info("To use this model in Render/Vercel, set:")
                    logger.info(f"  MODEL_PATH=gcp://{bucket_name}/{gcp_model_path}")
                    logger.info("")
                    logger.info("Or use bucket name from env var:")
                    logger.info(f"  MODEL_PATH=gcp://{gcp_model_path}")
                    logger.info("=" * 60)
                else:
                    logger.warning("⚠️  Failed to upload model to GCP (model will work locally)")
                    logger.warning(f"   Local model path: {best_model_path}")
            except Exception as gcp_error:
                logger.warning(f"⚠️  GCP not available, skipping upload: {str(gcp_error)}")
                logger.info(f"   Model saved locally at: {best_model_path}")
        except Exception as e:
            logger.warning(f"Failed to upload model to GCP: {str(e)}")
            logger.info(f"Model saved locally at: {best_model_path}")


if __name__ == '__main__':
    main() 

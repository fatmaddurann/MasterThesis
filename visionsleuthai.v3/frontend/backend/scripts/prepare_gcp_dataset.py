"""
Prepare GCP Dataset for YOLOv8 Training
Downloads images from GCP, organizes into train/val split, and creates YOLO format
"""
import os
import sys
from pathlib import Path
from typing import List, Dict
import json
import shutil
from sklearn.model_selection import train_test_split
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.gcp_connector import GCPConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GCPDatasetPreparer:
    """Prepare GCP dataset for YOLOv8 training"""
    
    def __init__(self, bucket_name: str = None):
        """Initialize with GCP bucket"""
        self.gcp = GCPConnector(bucket_name=bucket_name)
        self.bucket_name = bucket_name or os.getenv('GCP_BUCKET_NAME')
        
    def download_from_gcp(self, gcp_path: str, local_path: str):
        """Download file/folder from GCP"""
        try:
            # Check if it's a folder or file
            blobs = list(self.gcp.bucket.list_blobs(prefix=gcp_path))
            
            if not blobs:
                logger.warning(f"No files found at {gcp_path}")
                return []
            
            downloaded_files = []
            os.makedirs(local_path, exist_ok=True)
            
            for blob in blobs:
                # Get relative path
                relative_path = blob.name[len(gcp_path):].lstrip('/')
                if not relative_path:
                    continue
                
                local_file_path = os.path.join(local_path, relative_path)
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                
                # Download file
                blob.download_to_filename(local_file_path)
                downloaded_files.append(local_file_path)
                logger.debug(f"Downloaded: {blob.name} -> {local_file_path}")
            
            logger.info(f"Downloaded {len(downloaded_files)} files from {gcp_path}")
            return downloaded_files
            
        except Exception as e:
            logger.error(f"Failed to download from GCP {gcp_path}: {str(e)}")
            raise
    
    def prepare_yolo_dataset(
        self,
        gcp_raw_path: str = "data/raw",
        output_version: str = "v1",
        train_ratio: float = 0.8,
        val_ratio: float = 0.2,
        include_negative: bool = True
    ):
        """
        Prepare YOLO format dataset from GCP raw data
        
        Args:
            gcp_raw_path: GCP path to raw images (e.g., "data/raw")
            output_version: Dataset version (e.g., "v1")
            train_ratio: Training set ratio
            val_ratio: Validation set ratio
            include_negative: Include negative examples (toothbrush, baseball_bat)
        """
        # Local working directory
        work_dir = Path("data_prep")
        work_dir.mkdir(exist_ok=True)
        
        # Download raw data from GCP
        logger.info("Downloading raw data from GCP...")
        raw_local = work_dir / "raw"
        self.download_from_gcp(gcp_raw_path, str(raw_local))
        
        # Organize classes
        classes = []
        class_images = {}
        
        # Positive classes (knife, handgun)
        positive_classes = ['knife', 'handgun']
        for cls in positive_classes:
            cls_path = raw_local / cls
            if cls_path.exists():
                images = list(cls_path.glob("*.jpg")) + list(cls_path.glob("*.png"))
                if images:
                    classes.append(cls)
                    class_images[cls] = images
                    logger.info(f"Found {len(images)} images for class: {cls}")
        
        # Negative classes (toothbrush, baseball_bat)
        negative_classes = []
        if include_negative:
            negative_path = raw_local / "negative"
            if negative_path.exists():
                for neg_cls in ['toothbrush', 'baseball_bat']:
                    neg_cls_path = negative_path / neg_cls
                    if neg_cls_path.exists():
                        images = list(neg_cls_path.glob("*.jpg")) + list(neg_cls_path.glob("*.png"))
                        if images:
                            # Negative examples: empty labels (background only)
                            classes.append(f"negative_{neg_cls}")  # For tracking
                            class_images[f"negative_{neg_cls}"] = images
                            logger.info(f"Found {len(images)} negative examples: {neg_cls}")
                            negative_classes.append(neg_cls)
        
        if not classes:
            raise ValueError("No classes found! Check GCP paths.")
        
        # Create YOLO structure
        yolo_dir = work_dir / "yolo_dataset"
        train_dir = yolo_dir / "train"
        val_dir = yolo_dir / "val"
        
        train_images_dir = train_dir / "images"
        train_labels_dir = train_dir / "labels"
        val_images_dir = val_dir / "images"
        val_labels_dir = val_dir / "labels"
        
        for d in [train_images_dir, train_labels_dir, val_images_dir, val_labels_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Prepare class mapping (YOLO uses numeric IDs)
        # Positive classes get IDs, negative classes get empty labels
        class_to_id = {}
        yolo_classes = []
        
        for idx, cls in enumerate(positive_classes):
            if cls in class_images:
                class_to_id[cls] = idx
                yolo_classes.append(cls)
        
        logger.info(f"YOLO Classes: {yolo_classes}")
        logger.info(f"Class mapping: {class_to_id}")
        
        # Split and copy images
        all_train_images = []
        all_val_images = []
        
        for cls, images in class_images.items():
            if not images:
                continue
            
            # Check if it's a negative class
            is_negative = cls.startswith("negative_")
            
            # Split train/val
            train_imgs, val_imgs = train_test_split(
                images,
                test_size=val_ratio,
                random_state=42
            )
            
            # Copy training images
            for img_path in train_imgs:
                dest_img = train_images_dir / img_path.name
                shutil.copy2(img_path, dest_img)
                all_train_images.append(dest_img)
                
                # Create label file
                label_file = train_labels_dir / (img_path.stem + ".txt")
                if is_negative:
                    # Negative examples: empty label file (background only)
                    label_file.write_text("")
                else:
                    # Positive examples: need manual labeling or use existing labels
                    # For now, create placeholder (you'll need to label these)
                    if not label_file.exists():
                        # Placeholder - you need to add actual bounding boxes
                        logger.warning(f"Label file not found for {img_path.name}. You need to label this image!")
                        label_file.write_text("")  # Empty for now
            
            # Copy validation images
            for img_path in val_imgs:
                dest_img = val_images_dir / img_path.name
                shutil.copy2(img_path, dest_img)
                all_val_images.append(dest_img)
                
                # Create label file
                label_file = val_labels_dir / (img_path.stem + ".txt")
                if is_negative:
                    label_file.write_text("")
                else:
                    if not label_file.exists():
                        logger.warning(f"Label file not found for {img_path.name}. You need to label this image!")
                        label_file.write_text("")
        
        logger.info(f"Training images: {len(all_train_images)}")
        logger.info(f"Validation images: {len(all_val_images)}")
        
        # Create data.yaml
        data_yaml_path = yolo_dir / "data.yaml"
        self.create_data_yaml(
            str(data_yaml_path),
            yolo_classes,
            str(train_images_dir),
            str(val_images_dir)
        )
        
        # Upload to GCP
        logger.info("Uploading prepared dataset to GCP...")
        gcp_dataset_path = f"data/labeled/{output_version}"
        self.upload_to_gcp(str(yolo_dir), gcp_dataset_path)
        
        logger.info(f"Dataset prepared and uploaded to: {gcp_dataset_path}")
        logger.info(f"Local dataset at: {yolo_dir}")
        
        return {
            "local_path": str(yolo_dir),
            "gcp_path": gcp_dataset_path,
            "data_yaml": str(data_yaml_path),
            "classes": yolo_classes,
            "train_count": len(all_train_images),
            "val_count": len(all_val_images),
            "negative_classes": negative_classes
        }
    
    def create_data_yaml(self, output_path: str, classes: List[str], train_path: str, val_path: str):
        """Create YOLO data.yaml file"""
        import yaml
        
        data_config = {
            'path': str(Path(train_path).parent.absolute()),
            'train': 'train/images',
            'val': 'val/images',
            'nc': len(classes),
            'names': classes
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(data_config, f, default_flow_style=False)
        
        logger.info(f"Created data.yaml at {output_path}")
        logger.info(f"Classes: {classes}")
    
    def upload_to_gcp(self, local_path: str, gcp_path: str):
        """Upload directory to GCP"""
        local_dir = Path(local_path)
        
        # Find all files
        all_files = []
        for ext in ['.jpg', '.jpeg', '.png', '.txt', '.yaml', '.json']:
            all_files.extend(local_dir.rglob(f"*{ext}"))
            all_files.extend(local_dir.rglob(f"*{ext.upper()}"))
        
        logger.info(f"Uploading {len(all_files)} files to GCP...")
        
        for file_path in all_files:
            relative_path = file_path.relative_to(local_dir)
            gcp_file_path = f"{gcp_path}/{relative_path.as_posix()}"
            
            try:
                self.gcp.upload_file(str(file_path), gcp_file_path)
            except Exception as e:
                logger.error(f"Failed to upload {file_path}: {str(e)}")
        
        logger.info(f"Uploaded to GCP: {gcp_path}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Prepare GCP dataset for YOLOv8 training')
    parser.add_argument('--bucket', type=str, help='GCP bucket name')
    parser.add_argument('--gcp-path', type=str, default='data/raw',
                       help='GCP path to raw images')
    parser.add_argument('--version', type=str, default='v1',
                       help='Dataset version')
    parser.add_argument('--train-ratio', type=float, default=0.8,
                       help='Training set ratio')
    parser.add_argument('--include-negative', action='store_true',
                       help='Include negative examples')
    
    args = parser.parse_args()
    
    preparer = GCPDatasetPreparer(bucket_name=args.bucket)
    
    result = preparer.prepare_yolo_dataset(
        gcp_raw_path=args.gcp_path,
        output_version=args.version,
        train_ratio=args.train_ratio,
        val_ratio=1.0 - args.train_ratio,
        include_negative=args.include_negative
    )
    
    print("\n" + "="*50)
    print("Dataset Preparation Complete!")
    print("="*50)
    print(f"Classes: {result['classes']}")
    print(f"Training images: {result['train_count']}")
    print(f"Validation images: {result['val_count']}")
    print(f"Negative classes: {result['negative_classes']}")
    print(f"Local path: {result['local_path']}")
    print(f"GCP path: {result['gcp_path']}")
    print(f"Data YAML: {result['data_yaml']}")
    print("\nNext steps:")
    print("1. Label the images using LabelImg or similar tool")
    print("2. Re-run this script to update labels")
    print("3. Start training with: python models/train.py")


if __name__ == '__main__':
    main()


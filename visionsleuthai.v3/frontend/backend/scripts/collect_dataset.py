"""
Dataset Collection Script for Knife and Weapon Detection
Downloads images from internet and uploads to Google Cloud Storage
"""
import os
import sys
import requests
from pathlib import Path
from typing import List, Dict
import json
from datetime import datetime
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.gcp_connector import GCPConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetCollector:
    """Collect and organize dataset images for training"""
    
    def __init__(self, bucket_name: str = None):
        """Initialize with GCP bucket"""
        self.gcp = GCPConnector(bucket_name=bucket_name)
        self.bucket_name = bucket_name or os.getenv('GCP_BUCKET_NAME')
        
    def download_image(self, url: str, save_path: str) -> bool:
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded: {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download {url}: {str(e)}")
            return False
    
    def upload_to_gcp(self, local_path: str, gcp_path: str) -> str:
        """Upload image to GCP Storage"""
        try:
            self.gcp.upload_file(local_path, gcp_path)
            logger.info(f"Uploaded to GCP: {gcp_path}")
            return gcp_path
        except Exception as e:
            logger.error(f"Failed to upload to GCP: {str(e)}")
            raise
    
    def collect_from_urls(self, urls: List[Dict[str, str]], category: str = "knife"):
        """
        Collect images from list of URLs
        
        Args:
            urls: List of dicts with 'url' and optional 'label' keys
            category: Category name (knife, gun, etc.)
        """
        local_dir = Path(f"data/raw/{category}")
        local_dir.mkdir(parents=True, exist_ok=True)
        
        metadata = []
        
        for idx, item in enumerate(urls):
            url = item.get('url', item) if isinstance(item, dict) else item
            label = item.get('label', category) if isinstance(item, dict) else category
            
            # Generate filename
            filename = f"{category}_{idx:04d}.jpg"
            local_path = local_dir / filename
            
            # Download image
            if self.download_image(url, str(local_path)):
            # Upload to GCP (organized structure)
            gcp_path = f"data/raw/{category}/images/{filename}"
                try:
                    self.upload_to_gcp(str(local_path), gcp_path)
                    
                    # Save metadata
                    metadata.append({
                        'filename': filename,
                        'url': url,
                        'label': label,
                        'gcp_path': gcp_path,
                        'local_path': str(local_path),
                        'collected_at': datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Failed to upload {filename}: {str(e)}")
        
        # Save metadata
        metadata_path = local_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Upload metadata to GCP
        gcp_metadata_path = f"data/raw/{category}/metadata.json"
        self.gcp.upload_file(str(metadata_path), gcp_metadata_path)
        
        logger.info(f"Collected {len(metadata)} images for {category}")
        return metadata
    
    def download_from_roboflow(self, dataset_url: str, api_key: str = None):
        """
        Download dataset from Roboflow
        
        Args:
            dataset_url: Roboflow dataset URL or workspace/dataset format
            api_key: Roboflow API key (optional, can use env var ROBoflow_API_KEY)
        """
        try:
            from roboflow import Roboflow
            
            api_key = api_key or os.getenv('ROBOFLOW_API_KEY')
            if not api_key:
                raise ValueError("Roboflow API key required. Set ROBoflow_API_KEY env var or pass api_key parameter")
            
            rf = Roboflow(api_key=api_key)
            
            # Parse dataset URL (format: workspace/dataset/version)
            # Example: "knife-detection/knife-detection/1"
            parts = dataset_url.strip('/').split('/')
            if len(parts) >= 2:
                workspace = parts[0]
                dataset_name = parts[1]
                version = parts[2] if len(parts) > 2 else None
                
                project = rf.workspace(workspace).project(dataset_name)
                if version:
                    dataset = project.version(int(version))
                else:
                    dataset = project.version(1)  # Default to version 1
                
                # Download dataset
                dataset.download("yolo", location="data/roboflow")
                logger.info(f"Downloaded Roboflow dataset: {workspace}/{dataset_name}")
                
                # Upload to GCP
                self.upload_dataset_to_gcp("data/roboflow")
                
        except ImportError:
            logger.error("Roboflow package not installed. Install with: pip install roboflow")
        except Exception as e:
            logger.error(f"Failed to download from Roboflow: {str(e)}")
            raise
    
    def upload_dataset_to_gcp(self, local_dataset_path: str):
        """Upload entire dataset directory to GCP"""
        dataset_path = Path(local_dataset_path)
        
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset path not found: {local_dataset_path}")
        
        # Find all images
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        images = []
        
        for ext in image_extensions:
            images.extend(dataset_path.rglob(f"*{ext}"))
            images.extend(dataset_path.rglob(f"*{ext.upper()}"))
        
        logger.info(f"Found {len(images)} images in {local_dataset_path}")
        
        for img_path in images:
            # Preserve directory structure
            relative_path = img_path.relative_to(dataset_path)
            # Organize in data/labeled structure
            gcp_path = f"data/labeled/v1/{relative_path.as_posix()}"
            
            try:
                self.upload_to_gcp(str(img_path), gcp_path)
            except Exception as e:
                logger.error(f"Failed to upload {img_path}: {str(e)}")
        
        logger.info(f"Uploaded {len(images)} images to GCP")


def collect_knife_images_from_sources():
    """
    Example: Collect knife images from various sources
    You can add your own URLs here
    """
    collector = DatasetCollector()
    
    # Example URLs (replace with actual image URLs)
    knife_urls = [
        # Add your image URLs here
        # Example:
        # {'url': 'https://example.com/knife1.jpg', 'label': 'knife'},
        # {'url': 'https://example.com/knife2.jpg', 'label': 'knife'},
    ]
    
    if knife_urls:
        collector.collect_from_urls(knife_urls, category="knife")
    else:
        logger.warning("No URLs provided. Add image URLs to knife_urls list.")


def collect_gun_images_from_sources():
    """Collect gun images from various sources"""
    collector = DatasetCollector()
    
    gun_urls = [
        # Add your gun image URLs here
    ]
    
    if gun_urls:
        collector.collect_from_urls(gun_urls, category="gun")
    else:
        logger.warning("No URLs provided. Add image URLs to gun_urls list.")


def main():
    """Main function - customize based on your needs"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect dataset images for training')
    parser.add_argument('--category', type=str, default='knife', 
                       help='Category to collect (knife, gun, etc.)')
    parser.add_argument('--roboflow', type=str, 
                       help='Roboflow dataset URL (workspace/dataset/version)')
    parser.add_argument('--urls-file', type=str,
                       help='JSON file with list of URLs to download')
    parser.add_argument('--bucket', type=str,
                       help='GCP bucket name (overrides env var)')
    
    args = parser.parse_args()
    
    # Initialize collector
    collector = DatasetCollector(bucket_name=args.bucket)
    
    if args.roboflow:
        # Download from Roboflow
        collector.download_from_roboflow(args.roboflow)
    elif args.urls_file:
        # Load URLs from file
        with open(args.urls_file, 'r') as f:
            urls = json.load(f)
        collector.collect_from_urls(urls, category=args.category)
    else:
        logger.info("No source specified. Use --roboflow or --urls-file")
        logger.info("Example usage:")
        logger.info("  python collect_dataset.py --roboflow workspace/dataset/1")
        logger.info("  python collect_dataset.py --urls-file urls.json --category knife")


if __name__ == '__main__':
    main()


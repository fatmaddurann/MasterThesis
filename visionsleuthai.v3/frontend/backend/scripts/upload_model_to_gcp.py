#!/usr/bin/env python3
"""
Automatically upload trained model to GCP Storage
Usage: python scripts/upload_model_to_gcp.py [model_path] [gcp_path]
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.gcp_connector import GCPConnector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_latest_model():
    """Find the latest trained model in runs/detect directory"""
    runs_dir = Path("runs/detect")
    if not runs_dir.exists():
        return None
    
    # Find all best.pt files
    best_models = list(runs_dir.glob("*/weights/best.pt"))
    if not best_models:
        return None
    
    # Sort by modification time, get latest
    latest_model = max(best_models, key=lambda p: p.stat().st_mtime)
    return latest_model


def upload_model_to_gcp(local_model_path: str = None, gcp_model_path: str = None):
    """Upload model to GCP Storage"""
    try:
        # Get bucket name
        bucket_name = os.getenv("GCP_BUCKET_NAME", "crime-detection-data")
        logger.info(f"Using GCP bucket: {bucket_name}")
        
        # Initialize GCP connector
        gcp = GCPConnector(bucket_name=bucket_name)
        
        # Find model if not provided
        if not local_model_path:
            logger.info("Searching for latest trained model...")
            latest_model = find_latest_model()
            if not latest_model:
                logger.error("No trained model found. Please train a model first or provide model path.")
                logger.info("Expected location: runs/detect/*/weights/best.pt")
                return False
            local_model_path = str(latest_model)
            logger.info(f"Found latest model: {local_model_path}")
        
        # Check if local file exists
        if not os.path.exists(local_model_path):
            logger.error(f"Model file not found: {local_model_path}")
            return False
        
        # Generate GCP path if not provided
        if not gcp_model_path:
            # Extract model name from path (e.g., runs/detect/knife_detection_v1/weights/best.pt)
            path_parts = Path(local_model_path).parts
            if "runs" in path_parts and "detect" in path_parts:
                # Find the experiment name (directory after "detect")
                detect_idx = path_parts.index("detect")
                if detect_idx + 1 < len(path_parts):
                    exp_name = path_parts[detect_idx + 1]
                    gcp_model_path = f"models/trained/{exp_name}/best.pt"
                else:
                    gcp_model_path = "models/trained/latest/best.pt"
            else:
                # Use filename
                model_filename = os.path.basename(local_model_path)
                gcp_model_path = f"models/trained/latest/{model_filename}"
        
        logger.info(f"Uploading model to GCP...")
        logger.info(f"  Local: {local_model_path}")
        logger.info(f"  GCP:   {bucket_name}/{gcp_model_path}")
        
        # Upload model
        success = gcp.upload_model(local_model_path, gcp_model_path)
        
        if success:
            logger.info("=" * 60)
            logger.info("✅ Model successfully uploaded to GCP!")
            logger.info("=" * 60)
            logger.info(f"GCP Path: {gcp_model_path}")
            logger.info("")
            logger.info("Next steps:")
            logger.info("1. Set MODEL_PATH environment variable in Render/Vercel:")
            logger.info(f"   MODEL_PATH=gcp://{bucket_name}/{gcp_model_path}")
            logger.info("")
            logger.info("2. Redeploy your backend service")
            logger.info("=" * 60)
            return True
        else:
            logger.error("❌ Failed to upload model to GCP")
            return False
            
    except Exception as e:
        logger.error(f"Error uploading model to GCP: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload trained model to GCP Storage')
    parser.add_argument('--model-path', type=str, default=None,
                       help='Local path to model file (default: auto-detect latest)')
    parser.add_argument('--gcp-path', type=str, default=None,
                       help='GCP path for model (default: auto-generate from model path)')
    parser.add_argument('--bucket', type=str, default=None,
                       help='GCP bucket name (default: from GCP_BUCKET_NAME env var)')
    
    args = parser.parse_args()
    
    # Override bucket name if provided
    if args.bucket:
        os.environ['GCP_BUCKET_NAME'] = args.bucket
    
    # Upload model
    success = upload_model_to_gcp(args.model_path, args.gcp_path)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

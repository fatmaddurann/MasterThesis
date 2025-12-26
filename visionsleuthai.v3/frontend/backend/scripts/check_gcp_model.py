#!/usr/bin/env python3
"""
Check if model exists in GCP Storage
"""
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.gcp_connector import GCPConnector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_gcp_models():
    """Check what models exist in GCP Storage"""
    try:
        bucket_name = os.getenv("GCP_BUCKET_NAME", "crime-detection-data")
        logger.info(f"Checking GCP bucket: {bucket_name}")
        
        # Try to get credentials from service account key file
        credentials_path = None
        if os.path.exists("/etc/secrets/crime-detection-system-455511-6eb0681355fe.json"):
            credentials_path = "/etc/secrets/crime-detection-system-455511-6eb0681355fe.json"
        elif os.path.exists("crime-detection-system-455511-6eb0681355fe.json"):
            credentials_path = "crime-detection-system-455511-6eb0681355fe.json"
        elif os.getenv("GCP_SERVICE_ACCOUNT_KEY"):
            # Save env var to temp file
            import tempfile
            import json
            key_data = json.loads(os.getenv("GCP_SERVICE_ACCOUNT_KEY"))
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
            json.dump(key_data, temp_file)
            temp_file.close()
            credentials_path = temp_file.name
        
        if not credentials_path:
            logger.warning("⚠️  GCP credentials not found locally")
            logger.info("")
            logger.info("To check models in GCP, you can:")
            logger.info("1. Check Render backend logs (they show if model was uploaded)")
            logger.info("2. Use Google Cloud Console: https://console.cloud.google.com/storage")
            logger.info("3. Check bucket: crime-detection-data/models/trained/")
            logger.info("")
            logger.info("Based on backend logs, model is NOT uploaded yet.")
            logger.info("Model will be automatically uploaded after training.")
            return []
        
        gcp = GCPConnector(bucket_name=bucket_name, credentials_path=credentials_path)
        
        # Check common model paths
        model_paths = [
            "models/trained/knife_detection_v1/best.pt",
            "models/trained/handgun_knife_v1/best.pt",
            "models/trained/latest/best.pt",
            "models/production/current.pt",
        ]
        
        logger.info("=" * 60)
        logger.info("Checking for models in GCP Storage...")
        logger.info("=" * 60)
        
        found_models = []
        for model_path in model_paths:
            exists = gcp.model_exists(model_path)
            if exists:
                logger.info(f"✅ Found: {model_path}")
                found_models.append(model_path)
            else:
                logger.info(f"❌ Not found: {model_path}")
        
        # Also list all files in models/trained/ directory
        try:
            logger.info("")
            logger.info("Listing all files in models/trained/...")
            blobs = list(gcp.bucket.list_blobs(prefix="models/trained/"))
            if blobs:
                for blob in blobs:
                    logger.info(f"  📄 {blob.name} ({blob.size / (1024*1024):.2f} MB)")
            else:
                logger.info("  No files found in models/trained/")
        except Exception as e:
            logger.warning(f"Could not list files: {str(e)}")
        
        logger.info("=" * 60)
        
        if found_models:
            logger.info(f"✅ Found {len(found_models)} model(s) in GCP")
            logger.info("")
            logger.info("To use a model, set MODEL_PATH in Render/Vercel:")
            for model_path in found_models:
                logger.info(f"  MODEL_PATH=gcp://{bucket_name}/{model_path}")
        else:
            logger.info("❌ No models found in GCP Storage")
            logger.info("")
            logger.info("To upload a model:")
            logger.info("  1. Train a model: python models/train.py --use-gcp ...")
            logger.info("  2. Or use: python scripts/upload_model_to_gcp.py")
        
        logger.info("=" * 60)
        
        return found_models
        
    except Exception as e:
        logger.error(f"Error checking GCP models: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == '__main__':
    check_gcp_models()

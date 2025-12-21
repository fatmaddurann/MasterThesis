"""
Test GCP Connection Script
Verifies that GCP connector can access the bucket with the provided credentials
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


def test_gcp_connection(bucket_name: str = "crime-detection-data", credentials_path: str = None):
    """
    Test GCP connection and list bucket contents
    
    Args:
        bucket_name: GCP bucket name
        credentials_path: Path to service account JSON key file
    """
    try:
        logger.info("=" * 50)
        logger.info("Testing GCP Connection")
        logger.info("=" * 50)
        
        # Find credentials file if not provided
        if not credentials_path:
            # Try multiple possible locations
            possible_paths = [
                # Relative to project root
                Path(__file__).parent.parent.parent.parent / "crime-detection-system-455511-6eb0681355fe.json",
                # Relative to backend
                Path(__file__).parent.parent.parent / "crime-detection-system-455511-6eb0681355fe.json",
                # Absolute path from env
                os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            ]
            
            for path in possible_paths:
                if path and os.path.exists(path):
                    credentials_path = str(path)
                    logger.info(f"Found credentials at: {credentials_path}")
                    break
        
        if credentials_path and not os.path.exists(credentials_path):
            logger.warning(f"Credentials file not found at: {credentials_path}")
            logger.info("Trying default authentication...")
            credentials_path = None
        
        # Initialize GCP connector
        logger.info(f"Initializing GCP connector with bucket: {bucket_name}")
        if credentials_path:
            logger.info(f"Using credentials: {credentials_path}")
        
        gcp = GCPConnector(bucket_name=bucket_name, credentials_path=credentials_path)
        
        # Test 1: List files in bucket
        logger.info("\n" + "=" * 50)
        logger.info("Test 1: Listing bucket contents")
        logger.info("=" * 50)
        
        files = gcp.list_files()
        logger.info(f"Found {len(files)} files/folders in bucket")
        
        # Show top-level structure
        top_level = set()
        for file_path in files[:50]:  # Limit to first 50 for display
            parts = file_path.split('/')
            if parts:
                top_level.add(parts[0])
        
        logger.info(f"Top-level folders/files: {sorted(top_level)}")
        
        # Test 2: Check specific paths
        logger.info("\n" + "=" * 50)
        logger.info("Test 2: Checking dataset structure")
        logger.info("=" * 50)
        
        dataset_paths = [
            "data/raw/knife",
            "data/raw/handgun",
            "data/raw/negative/toothbrush",
            "data/raw/negative/baseball_bat"
        ]
        
        for path in dataset_paths:
            matching_files = [f for f in files if f.startswith(path)]
            if matching_files:
                logger.info(f"✅ {path}: {len(matching_files)} files found")
                # Show first few files
                for f in matching_files[:3]:
                    logger.info(f"   - {f}")
            else:
                logger.warning(f"❌ {path}: No files found")
        
        # Test 3: Test upload/download (optional)
        logger.info("\n" + "=" * 50)
        logger.info("Test 3: Connection status")
        logger.info("=" * 50)
        logger.info("✅ GCP Connection successful!")
        logger.info(f"✅ Bucket: {bucket_name}")
        logger.info(f"✅ Total files: {len(files)}")
        
        return True
        
    except Exception as e:
        logger.error("=" * 50)
        logger.error("GCP Connection Failed!")
        logger.error("=" * 50)
        logger.error(f"Error: {str(e)}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Check if credentials file exists and is valid")
        logger.error("2. Verify bucket name is correct")
        logger.error("3. Ensure service account has Storage Admin role")
        logger.error("4. Check network connectivity")
        return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test GCP connection')
    parser.add_argument('--bucket', type=str, default='crime-detection-data',
                       help='GCP bucket name')
    parser.add_argument('--credentials', type=str,
                       help='Path to service account JSON key file')
    
    args = parser.parse_args()
    
    success = test_gcp_connection(
        bucket_name=args.bucket,
        credentials_path=args.credentials
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()


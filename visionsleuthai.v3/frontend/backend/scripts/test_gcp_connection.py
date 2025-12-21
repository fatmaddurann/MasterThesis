"""
Test GCP Connection Script
Tests if GCP credentials and bucket access are working correctly
"""
import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.gcp_connector import GCPConnector

def test_gcp_connection():
    """Test GCP connection and bucket access"""
    print("=" * 50)
    print("GCP Connection Test")
    print("=" * 50)
    
    # Check environment variables
    print("\n1. Checking Environment Variables...")
    bucket_name = os.getenv('GCP_BUCKET_NAME')
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if bucket_name:
        print(f"   ✅ GCP_BUCKET_NAME: {bucket_name}")
    else:
        print("   ❌ GCP_BUCKET_NAME not set")
        print("   💡 Set it with: export GCP_BUCKET_NAME='crime-detection-data'")
        return False
    
    if creds_path:
        print(f"   ✅ GOOGLE_APPLICATION_CREDENTIALS: {creds_path}")
        if os.path.exists(creds_path):
            print(f"   ✅ Credentials file exists")
        else:
            print(f"   ❌ Credentials file not found at: {creds_path}")
            return False
    else:
        print("   ⚠️  GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   💡 Google Cloud SDK will try to use default credentials")
        print("   💡 Or set it with: export GOOGLE_APPLICATION_CREDENTIALS='/path/to/key.json'")
    
    # Test connection
    print("\n2. Testing GCP Connection...")
    try:
        gcp = GCPConnector(bucket_name=bucket_name)
        print("   ✅ GCPConnector initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed to initialize GCPConnector: {str(e)}")
        print("\n   💡 Troubleshooting:")
        print("      - Check if credentials file exists and is valid JSON")
        print("      - Verify service account has Storage Admin role")
        print("      - Check bucket name is correct")
        return False
    
    # Test bucket access
    print("\n3. Testing Bucket Access...")
    try:
        files = gcp.list_files()
        print(f"   ✅ Bucket access successful!")
        print(f"   📁 Found {len(files)} files/folders in bucket")
        
        if files:
            print("\n   Sample files/folders:")
            for f in files[:10]:  # Show first 10
                print(f"      - {f}")
            if len(files) > 10:
                print(f"      ... and {len(files) - 10} more")
    except Exception as e:
        print(f"   ❌ Failed to access bucket: {str(e)}")
        print("\n   💡 Troubleshooting:")
        print("      - Verify service account has Storage Admin role")
        print("      - Check bucket name: crime-detection-data")
        print("      - Verify bucket exists in your GCP project")
        return False
    
    # Test specific paths
    print("\n4. Testing Dataset Paths...")
    test_paths = [
        "data/raw/knife",
        "data/raw/handgun",
        "data/raw/negative/toothbrush",
        "data/raw/negative/baseball_bat"
    ]
    
    for path in test_paths:
        try:
            blobs = list(gcp.bucket.list_blobs(prefix=path, max_results=1))
            if blobs:
                print(f"   ✅ {path}: Found files")
            else:
                print(f"   ⚠️  {path}: No files found (this is OK if you haven't uploaded yet)")
        except Exception as e:
            print(f"   ❌ {path}: Error - {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ GCP Connection Test Complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. If all tests passed, you're ready to use GCP scripts")
    print("2. Run: python scripts/prepare_gcp_dataset.py --bucket crime-detection-data")
    print("3. Check setup_gcp_credentials.md for detailed setup instructions")
    
    return True

if __name__ == '__main__':
    success = test_gcp_connection()
    sys.exit(0 if success else 1)

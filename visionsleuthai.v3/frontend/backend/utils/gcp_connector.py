import os
from google.cloud import storage
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GCPConnector:
    _instance = None
    _bucket = None

    def __new__(cls, bucket_name: str = None, credentials_path: str = None):
        if cls._instance is None:
            cls._instance = super(GCPConnector, cls).__new__(cls)
            # Bucket name'i environment variable'dan al veya default kullan
            cls._instance.bucket_name = bucket_name or os.getenv('GCP_BUCKET_NAME', 'crime-detection-data')
            
            # Credentials: Try multiple methods (priority order)
            # 1. GCP_SERVICE_ACCOUNT_KEY env var (JSON string for production)
            # 2. Render secret files path (if secret file is uploaded)
            # 3. GOOGLE_APPLICATION_CREDENTIALS env var (file path)
            # 4. credentials_path parameter
            # 5. Default file path (local development)
            
            creds_path = None
            creds_json = None
            
            # Method 1: Check for JSON string in environment variable (for production)
            gcp_key_json = os.getenv('GCP_SERVICE_ACCOUNT_KEY')
            if gcp_key_json:
                try:
                    # Try to parse as JSON (might be base64 encoded)
                    import base64
                    try:
                        # Try base64 decode first
                        decoded = base64.b64decode(gcp_key_json)
                        creds_json = json.loads(decoded.decode('utf-8'))
                    except:
                        # If not base64, try direct JSON
                        creds_json = json.loads(gcp_key_json)
                    logger.info("GCP credentials found in GCP_SERVICE_ACCOUNT_KEY environment variable")
                except Exception as e:
                    logger.warning(f"Failed to parse GCP_SERVICE_ACCOUNT_KEY: {str(e)}")
            
            # Method 2: Check Render secret files (Render mounts secret files at /etc/secrets/)
            if not creds_json:
                # Render secret files are typically mounted at /etc/secrets/ or specified path
                render_secret_path = os.getenv('RENDER_SECRET_FILE_PATH', '/etc/secrets')
                secret_file_name = os.getenv('GCP_SECRET_FILE_NAME', 'crime-detection-system-455511-6eb0681355fe.json')
                
                # Try common Render secret file locations
                render_secret_paths = [
                    os.path.join(render_secret_path, secret_file_name),  # Custom path or default /etc/secrets/
                    os.path.join('/etc/secrets', secret_file_name),     # Default Render path
                    os.path.join('/secrets', secret_file_name),         # Alternative Render path
                    os.path.join(os.getcwd(), secret_file_name),       # Current directory
                ]
                
                for test_path in render_secret_paths:
                    if os.path.exists(test_path):
                        creds_path = test_path
                        logger.info(f"GCP credentials found in Render secret file: {creds_path}")
                        break
            
            # Method 3: Check for file path in environment variable
            if not creds_json and not creds_path:
                creds_path = (
                    credentials_path or 
                    os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                )
                
                # Method 4: Try default file path (local development)
                if not creds_path:
                    base_path1 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    base_path2 = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..')
                    default_paths = [
                        os.path.join(base_path1, 'crime-detection-system-455511-6eb0681355fe.json'),
                        os.path.join(base_path2, 'crime-detection-system-455511-6eb0681355fe.json')
                    ]
                    for test_path in default_paths:
                        if os.path.exists(test_path):
                            creds_path = test_path
                            break
            
            try:
                # Initialize client with credentials
                if creds_json:
                    # Use JSON credentials directly (production - Vercel/Render env var)
                    cls._instance.client = storage.Client.from_service_account_info(creds_json)
                    logger.info("GCPConnector initialized with JSON credentials from GCP_SERVICE_ACCOUNT_KEY environment variable")
                elif creds_path and os.path.exists(creds_path):
                    # Use file path (Render secret files or local development)
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
                    cls._instance.client = storage.Client.from_service_account_json(creds_path)
                    # Detect if it's Render secret file
                    if '/etc/secrets' in creds_path or '/secrets' in creds_path:
                        logger.info(f"GCPConnector initialized with Render secret file: {creds_path}")
                    else:
                        logger.info(f"GCPConnector initialized with credentials file: {creds_path}")
                else:
                    # Try default authentication (uses GOOGLE_APPLICATION_CREDENTIALS env var or default credentials)
                    cls._instance.client = storage.Client()
                    logger.warning("GCPConnector initialized with default authentication (credentials not found)")
                    logger.warning("This may fail in production. Please set GCP_SERVICE_ACCOUNT_KEY (Vercel) or upload secret file (Render)")
                
                cls._instance.bucket = cls._instance.client.bucket(cls._instance.bucket_name)
                logger.info(f"GCPConnector initialized with bucket: {cls._instance.bucket_name}")
                
                # Test connection by listing bucket (optional, can be disabled for faster startup)
                try:
                    # Quick test: try to access bucket metadata
                    cls._instance.bucket.reload()
                    logger.info("GCP bucket connection verified successfully")
                except Exception as test_error:
                    logger.warning(f"GCP bucket connection test failed (may still work): {str(test_error)}")
                    
            except Exception as e:
                logger.error(f"Failed to initialize GCPConnector: {str(e)}")
                logger.error("Please check:")
                logger.error("  - Render: Secret file uploaded and GCP_BUCKET_NAME set?")
                logger.error("  - Vercel: GCP_SERVICE_ACCOUNT_KEY and GCP_BUCKET_NAME environment variables set?")
                raise
        return cls._instance

    def upload_file(self, source_file_name: str, destination_blob_name: str):
        """Uploads a file to the bucket."""
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print(f"File {source_file_name} uploaded to {destination_blob_name}.")

    def download_file(self, source_blob_name: str, destination_file_name: str):
        """Downloads a blob from the bucket."""
        blob = self.bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")

    def list_files(self):
        """Lists all the blobs in the bucket."""
        blobs = self.bucket.list_blobs()
        return [blob.name for blob in blobs]

    def upload_video(self, local_path: str) -> str:
        """Upload video to GCP Storage and return the GCP path"""
        try:
            # Generate a unique path in GCP
            filename = os.path.basename(local_path)
            gcp_path = f"videos/{datetime.utcnow().strftime('%Y/%m/%d')}/{filename}"
            
            # Upload the file
            blob = self.bucket.blob(gcp_path)
            blob.upload_from_filename(local_path)
            
            logger.info(f"Video uploaded to GCP: {gcp_path}")
            return gcp_path
            
        except Exception as e:
            logger.error(f"Error uploading video to GCP: {str(e)}")
            raise Exception(f"Failed to upload video to GCP: {str(e)}")
    
    def save_results(self, video_id: str, results: dict) -> str:
        """Save analysis results to GCP Storage and return the results path"""
        try:
            # Generate a unique path for results
            results_path = f"results/{video_id}/analysis.json"
            
            # Save results as JSON
            blob = self.bucket.blob(results_path)
            blob.upload_from_string(
                json.dumps(results),
                content_type='application/json'
            )
            
            logger.info(f"Results saved to GCP: {results_path}")
            return results_path
            
        except Exception as e:
            logger.error(f"Error saving results to GCP: {str(e)}")
            raise Exception(f"Failed to save results to GCP: {str(e)}")
    
    def get_results(self, results_path: str) -> dict:
        """Get analysis results from GCP Storage"""
        try:
            blob = self.bucket.blob(results_path)
            content = blob.download_as_string()
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error getting results from GCP: {str(e)}")
            raise Exception(f"Failed to get results from GCP: {str(e)}")
    
    def generate_signed_url(self, gcp_path: str, expiration: int = 3600) -> str:
        """Generate a signed URL for temporary access to a file"""
        try:
            blob = self.bucket.blob(gcp_path)
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.utcnow() + timedelta(seconds=expiration),
                method="GET"
            )
            return url
            
        except Exception as e:
            logger.error(f"Error generating signed URL: {str(e)}")
            raise Exception(f"Failed to generate signed URL: {str(e)}") 

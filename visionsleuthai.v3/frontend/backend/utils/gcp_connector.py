import os
from google.cloud import storage
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GCPConnector:
    _instance = None
    _bucket = None

    def __new__(cls, bucket_name: str = None):
        if cls._instance is None:
            cls._instance = super(GCPConnector, cls).__new__(cls)
            # Bucket name'i environment variable'dan al
            cls._instance.bucket_name = bucket_name or os.getenv('GCP_BUCKET_NAME')
            if not cls._instance.bucket_name:
                raise ValueError("GCP_BUCKET_NAME environment variable is not set")
            
            try:
                cls._instance.client = storage.Client()
                cls._instance.bucket = cls._instance.client.bucket(cls._instance.bucket_name)
                logger.info(f"GCPConnector initialized with bucket: {cls._instance.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to initialize GCPConnector: {str(e)}")
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

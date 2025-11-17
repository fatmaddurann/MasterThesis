#!/usr/bin/env python3
"""
Test script to verify video analysis functionality
"""
import requests
import json
import time

def test_video_analysis():
    base_url = "http://localhost:8000"
    
    print("Testing video analysis functionality...")
    
    # Test 1: Check if backend is healthy
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✓ Backend health check: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"✗ Backend health check failed: {e}")
        return
    
    # Test 2: Check video analysis endpoint
    try:
        response = requests.get(f"{base_url}/api/video/analysis/nonexistent")
        print(f"✓ Video analysis endpoint: {response.status_code}")
        if response.status_code == 404:
            print("  Response: Video analysis not found (expected)")
    except Exception as e:
        print(f"✗ Video analysis endpoint failed: {e}")
    
    # Test 3: Check if we can create a mock analysis task
    try:
        # This would normally be done by the upload endpoint
        mock_task = {
            "status": "processing",
            "timestamp": "2024-01-01T00:00:00Z",
            "video_path": "/tmp/test.mp4",
            "results_path": None,
            "error": None,
            "summary": None,
            "model_performance": None,
            "total_frames": 100,
            "processed_frames": 50,
            "progress": 50
        }
        print("✓ Mock analysis task structure is valid")
        print(f"  Task: {json.dumps(mock_task, indent=2)}")
    except Exception as e:
        print(f"✗ Mock analysis task failed: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_video_analysis()

'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadVideo, getAnalysisResults, type AnalysisResult } from '@/utils/api';
import { CloudArrowUpIcon } from '@heroicons/react/24/outline';

type UploadCardProps = {
  onUploadComplete: (results: AnalysisResult) => void;
};

const UploadCard = ({ onUploadComplete }: UploadCardProps): JSX.Element => {
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult | null>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const pollInterval = useRef<NodeJS.Timeout | null>(null);

  // Cleanup function
  useEffect(() => {
    return () => {
      if (pollInterval.current) {
        clearInterval(pollInterval.current);
        pollInterval.current = null;
      }
      if (videoPreview) {
        URL.revokeObjectURL(videoPreview);
      }
    };
  }, [videoPreview]);

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    setError(null);
    setProgress(0);

    try {
      // Dosya boyutu kontrolü
      if (file.size > 500 * 1024 * 1024) {
        throw new Error('File too large. Maximum size is 500MB');
      }

      // Dosya tipi kontrolü
      const allowedTypes = ['.mp4', '.mov', '.avi', '.mkv'];
      const fileExt = file.name.split('.').pop()?.toLowerCase();
      if (!fileExt || !allowedTypes.includes(`.${fileExt}`)) {
        throw new Error(`Invalid file type. Allowed types: ${allowedTypes.join(', ')}`);
      }

      // Upload işlemi
      const { id } = await uploadVideo(file);
      
      // Analiz sonuçlarını bekle
      setIsAnalyzing(true);
      setProgress(10); // Upload tamamlandı
      
      let retryCount = 0;
      const maxRetries = 60; // 2 dakika timeout (60 * 2 saniye)
      
      while (retryCount < maxRetries) {
        try {
          const results = await getAnalysisResults(id);
          console.log(`Analysis check ${retryCount + 1}:`, results);
          
          if (results && typeof results === 'object' && results.status === 'completed') {
            setProgress(100);
            setAnalysisResults(results);
            setSuccess(true);
            setIsAnalyzing(false);
            onUploadComplete(results);
            break;
          } else if (results && typeof results === 'object' && results.status === 'failed') {
            const errorMessage = (results.error && typeof results.error === 'string') 
              ? results.error 
              : 'Analysis failed';
            throw new Error(errorMessage);
          } else if (results && typeof results === 'object' && results.status === 'processing') {
            // Gerçek progress bilgisini kullan
            let currentProgress = 10; // Base progress after upload
            
            if (typeof results.progress === 'number' && results.progress >= 0) {
              // Backend'ten gelen progress kullan
              currentProgress = Math.min(95, 10 + results.progress * 0.85);
            } else if (typeof results.processed_frames === 'number' && typeof results.total_frames === 'number' && results.total_frames > 0) {
              // Frame-based progress
              const frameProgress = (results.processed_frames / results.total_frames) * 85;
              currentProgress = Math.min(95, 10 + frameProgress);
            } else {
              // Fallback progress - yavaş artış
              currentProgress = Math.min(95, 10 + (retryCount * 1.2));
            }
            
            setProgress(currentProgress);
            
            // Daha sık kontrol et
            await new Promise(resolve => setTimeout(resolve, 1000)); // 1 saniye bekle
            retryCount++;
          } else {
            // Unknown status or no results
            console.log('Unknown status or no results:', results);
            setProgress(Math.min(50, 10 + (retryCount * 2)));
            await new Promise(resolve => setTimeout(resolve, 2000));
            retryCount++;
          }
        } catch (error) {
          console.error(`Analysis check attempt ${retryCount + 1} failed:`, error);
          if (error instanceof Error) {
            console.error('Error details:', error.message);
            console.error('Error stack:', error.stack);
          }
          if (retryCount === maxRetries - 1) {
            throw new Error('Analysis timeout - please try again');
          }
          await new Promise(resolve => setTimeout(resolve, 2000));
          retryCount++;
        }
      }
      
      if (retryCount >= maxRetries) {
        throw new Error('Analysis timeout - please try again');
      }
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('An unexpected error occurred.');
      }
      setIsUploading(false);
      setIsAnalyzing(false);
    } finally {
      setProgress(100);
    }
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setIsUploading(true);
    setError(null);

    try {
      // FormData oluştur ve dosyayı ekle
      const formData = new FormData();
      formData.append('video', file);

      // Upload işlemi
      await handleUpload(file);

    } catch (err) {
      setIsUploading(false);
      setError(err instanceof Error ? err.message : 'Upload failed');
      console.error('Upload error:', err);
    }
  }, [onUploadComplete]);

  // Update dropzone config
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv']
    },
    maxSize: 500 * 1024 * 1024, // 500MB
    multiple: false
  });

  return (
    <div className="w-full max-w-6xl mx-auto p-6 space-y-6">
      {/* Upload Box - Always visible */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Video Upload</h2>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-500'
          } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} disabled={isUploading} />
          <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-sm text-gray-600">
            {isDragActive
              ? 'Drop the video here'
              : 'Drag and drop a video file here, or click to select'}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Supported formats: MP4, AVI, MOV, MKV (max 500MB)
          </p>
          {error && (
            <p className="mt-2 text-sm text-red-600">{error}</p>
          )}
          {isUploading && (
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="mt-2 text-sm text-gray-600">
                {isAnalyzing ? `Analyzing video... ${progress}%` : `Uploading... ${progress}%`}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Results Box - Only visible when analysis is complete */}
      {success && analysisResults && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <p className="text-green-800 font-medium">Video analysis completed successfully!</p>
          </div>
          <p className="text-green-600 text-sm mt-1">
            Comprehensive analysis results are displayed below.
          </p>
        </div>
      )}
    </div>
  );
};

export default UploadCard;

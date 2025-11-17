import React, { useState } from 'react';

interface CameraCardProps {
  onStartAnalysis: () => void;
  onStopAnalysis: () => void;
  isAnalyzing: boolean;
  error: string | null;
  videoRef: React.RefObject<HTMLVideoElement>;
  overlayRef: React.RefObject<HTMLCanvasElement>;
  onCameraReady: () => void;
  onCameraStop: () => void;
}

export function CameraCard({ onStartAnalysis, onStopAnalysis, isAnalyzing, error, videoRef, overlayRef, onCameraReady, onCameraStop }: CameraCardProps) {
  const [cameraStarted, setCameraStarted] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);

  const handleStartCamera = async () => {
    setLocalError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setStream(stream);
      setCameraStarted(true);
      onCameraReady();
    } catch (err) {
      setLocalError('You must allow camera access to use this feature.');
    }
  };

  const handleStopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      if (videoRef.current) videoRef.current.srcObject = null;
      setStream(null);
    }
    setCameraStarted(false);
    onCameraStop();
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden mb-4 w-full max-w-xl flex items-center justify-center">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-full object-cover"
          style={{ background: '#000', minHeight: 320 }}
        />
        {/* Overlay Canvas */}
        <canvas
          ref={overlayRef}
          className="absolute top-0 left-0 w-full h-full pointer-events-none"
          style={{ zIndex: 10 }}
        />
      </div>
      {!cameraStarted ? (
        <button
          onClick={handleStartCamera}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors mb-2"
        >
          Start Camera
        </button>
      ) : (
        <div className="flex gap-2 mb-2">
          <button
            onClick={handleStopCamera}
            className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Stop Camera
          </button>
          {!isAnalyzing ? (
            <button
              onClick={onStartAnalysis}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Start Analysis
            </button>
          ) : (
            <button
              onClick={onStopAnalysis}
              className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Stop Analysis
            </button>
          )}
        </div>
      )}
      {(error || localError) && (
        <div className="mt-2 p-3 bg-red-100 text-red-700 rounded-lg text-sm">
          {error || localError}
        </div>
      )}
    </div>
  );
} 
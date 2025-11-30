'use client';

import { useState, useRef, useEffect } from 'react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { CameraCard } from '@/components/CameraCard';
import ForensicLiveAnalysisBox from '@/components/forensic/ForensicLiveAnalysisBox';
import jsPDF from 'jspdf';
import ForensicDashboard from '@/components/forensic/ForensicDashboard';
import { useForensicAnalysis } from '@/components/forensic/useForensicAnalysis';
import { LiveAnalysisResults } from '@/components/forensic/LiveAnalysisResults';
import { ForensicAnalysisResults, DetectionWithTimestamp } from '@/components/forensic/ForensicAnalysisResults';
import { sendFrame } from '@/utils/api';

// Tip tanımları
interface Detection {
  type: string;
  confidence: number;
  bbox: [number, number, number, number];
  timestamp: string;
  risk: 'High' | 'Medium' | 'Low';
}

interface AnalysisResult {
  timestamp: string;
  detections: Detection[];
}

// ForensicDashboard için veri dönüşüm fonksiyonu
type ForensicReport = {
  crimeAnalysis: {
    temporalAnalysis: { eventTimeline: any[] };
    spatialMapping: { hotSpotCoordinates: any[] };
  };
  forensicVisualizations: any;
  expertOpinion: any;
};

const transformResultsForDashboard = (results: AnalysisResult[]): ForensicReport => {
  const eventTimeline = results.flatMap(result =>
    result.detections.map(det => ({
      timestamp: result.timestamp,
      eventType: det.type,
      confidence: det.confidence / 100,
      evidentiaryValue: det.confidence > 80 ? 'high' : det.confidence > 60 ? 'medium' : 'low',
    }))
  );
  const hotSpotCoordinates = results.flatMap(result =>
    result.detections.map(det => ({
      x: det.bbox[0],
      y: det.bbox[1],
      crimeType: det.type,
      intensity: det.confidence / 100,
    }))
  );
  return {
    crimeAnalysis: {
      temporalAnalysis: { eventTimeline },
      spatialMapping: { hotSpotCoordinates },
    },
    forensicVisualizations: {},
    expertOpinion: {},
  };
};

// Risk değerlendirme fonksiyonu
const assessRisk = (detection: any): 'High' | 'Medium' | 'Low' => {
  const type = (detection.type || detection.class_name || '').toLowerCase();
  const confidence = detection.confidence;

  // Yüksek riskli nesneler
  const highRiskItems = ['gun', 'knife', 'weapon', 'rifle', 'pistol', 'firearm'];
  // Orta riskli nesneler
  const mediumRiskItems = ['bottle', 'scissors', 'hammer', 'baseball bat', 'crowbar'];

  if (highRiskItems.some(item => type.includes(item))) {
    return confidence > 0.7 ? 'High' : 'Medium';
  }
  if (mediumRiskItems.some(item => type.includes(item))) {
    return confidence > 0.8 ? 'Medium' : 'Low';
  }
  return 'Low';
};

// Canvas üzerine tespitleri çizme fonksiyonu
function drawDetectionsOnCanvas(canvas: HTMLCanvasElement, detections: Detection[], videoElement: HTMLVideoElement | null) {
  if (!canvas || !videoElement || videoElement.videoWidth === 0) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // Canvas boyutunu video element'in display boyutuna ayarla (CSS ile ölçeklenmiş)
  const rect = videoElement.getBoundingClientRect();
  const displayWidth = rect.width;
  const displayHeight = rect.height;
  const videoWidth = videoElement.videoWidth;
  const videoHeight = videoElement.videoHeight;
  
  // Canvas'ı display boyutuna ayarla
  canvas.width = displayWidth;
  canvas.height = displayHeight;
  
  // Scale faktörlerini hesapla
  const scaleX = displayWidth / videoWidth;
  const scaleY = displayHeight / videoHeight;

  // Canvas'ı temizle (transparent overlay)
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  detections.forEach((det) => {
    const typeLower = det.type.toLowerCase();
    
    // Person, nesne ve tehlikeli nesne için farklı renkler
    let color, strokeColor;
    if (typeLower === 'person' || typeLower === 'people') {
      // Person için mavi
      color = 'rgba(0, 100, 255, 0.3)';
      strokeColor = 'rgba(0, 150, 255, 1)';
    } else if (['gun', 'knife', 'weapon', 'pistol', 'rifle', 'firearm', 'machete', 'axe', 'scissors', 'hammer', 'baseball_bat', 'crowbar'].some(d => typeLower.includes(d))) {
      // Tehlikeli nesneler için kırmızı
      color = 'rgba(255, 0, 0, 0.4)';
      strokeColor = 'rgba(255, 50, 50, 1)';
    } else {
      // Diğer nesneler için sarı
      color = 'rgba(255, 255, 0, 0.3)';
      strokeColor = 'rgba(255, 200, 0, 1)';
    }

    // Risk seviyesine göre renk ayarı (tehlikeli nesneler için)
    if (det.risk === 'High') {
      color = 'rgba(255, 0, 0, 0.5)';
      strokeColor = 'rgba(255, 0, 0, 1)';
    } else if (det.risk === 'Medium') {
      color = 'rgba(255, 165, 0, 0.4)';
      strokeColor = 'rgba(255, 140, 0, 1)';
    }

    // Bounding box koordinatlarını scale et
    const [x1, y1, x2, y2] = det.bbox;
    const scaledX1 = x1 * scaleX;
    const scaledY1 = y1 * scaleY;
    const scaledX2 = x2 * scaleX;
    const scaledY2 = y2 * scaleY;
    const width = scaledX2 - scaledX1;
    const height = scaledY2 - scaledY1;
    
    // Arka plan (doldurulmuş)
    ctx.fillStyle = color;
    ctx.fillRect(scaledX1, scaledY1, width, height);
    
    // Kenar çizgisi
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = 3;
    ctx.strokeRect(scaledX1, scaledY1, width, height);

    // Etiket hazırlama
    const confidencePercent = Math.round(det.confidence * 100);
    let label = `${det.type} (${confidencePercent}%)`;
    
    // Güven puanı varsa göster
    const securityScore = (det as any).security_score;
    if (securityScore !== undefined) {
      label += ` | Security: ${Math.round(securityScore * 100)}%`;
    }
    
    // Risk nedeni varsa göster
    const riskReason = (det as any).risk_reason;
    if (riskReason) {
      label += ` | ${riskReason}`;
    }

    ctx.font = 'bold 14px Arial';
    const textWidth = ctx.measureText(label).width;
    const labelHeight = 25;
    
    // Etiket arka planı
    ctx.fillStyle = strokeColor;
    ctx.fillRect(scaledX1, scaledY1 - labelHeight, textWidth + 10, labelHeight);

    // Etiket metni
    ctx.fillStyle = 'white';
    ctx.fillText(label, scaledX1 + 5, scaledY1 - 8);
  });
}

export default function LiveAnalysisPage() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [cameraStarted, setCameraStarted] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [frameResults, setFrameResults] = useState<DetectionWithTimestamp[]>([]);
  const [currentDetections, setCurrentDetections] = useState<Detection[]>([]);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Kamera başlat
  const startCamera = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "environment"
        } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setCameraStarted(true);
      }
    } catch (err) {
      setError('Kamera erişimi reddedildi veya kullanılamıyor.');
      console.error('Camera error:', err);
    }
  };

  // Kamera durdur
  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => {
        track.stop();
        stream.removeTrack(track);
      });
      videoRef.current.srcObject = null;
      setCameraStarted(false);
      setIsAnalyzing(false);
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  // Her 1000ms'de bir frame'i backend'e POST et
  useEffect(() => {
    if (!isAnalyzing || !cameraStarted) return;

    const processAndSendFrame = async () => {
      if (!videoRef.current || !videoRef.current.srcObject) return;

      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      try {
        ctx.drawImage(videoRef.current, 0, 0);
        
        // Compress the image before sending
        const imageData = canvas.toDataURL('image/jpeg', 0.7);
        
        // Use the sendFrame function from api.ts which handles API URL correctly
        const data = await sendFrame(imageData);
        const now = new Date().toLocaleString();
        
        // Tespitleri işle ve risk değerlendirmesi yap
        const detections = (data.detections || []).map((det: any) => ({
          type: det.type || det.class_name,
          confidence: det.confidence,
          bbox: det.bbox || [0,0,0,0],
          timestamp: now,
          risk: assessRisk(det),
          security_score: det.security_score,
          risk_reason: det.risk_reason,
          risk_adjusted: det.risk_adjusted
        }));
        
        // Yüksek riskli tespitleri kontrol et
        const highRiskDetections = detections.filter((d: Detection) => d.risk === 'High');
        if (highRiskDetections.length > 0) {
          console.warn('High risk detection:', highRiskDetections);
          // Burada gerekirse alarm veya bildirim tetiklenebilir
        }

        setFrameResults(prev => [...detections, ...prev].slice(0, 100));
        setCurrentDetections(detections); // Güncel tespitleri state'e kaydet
        setError(null);

        // Tespitleri video üzerine çiz
        if (canvasRef.current && videoRef.current && videoRef.current.videoWidth > 0) {
          // Video hazır olduğunda çiz
          requestAnimationFrame(() => {
            if (canvasRef.current && videoRef.current) {
              drawDetectionsOnCanvas(canvasRef.current, detections, videoRef.current);
            }
          });
        }

      } catch (e) {
        console.error('Frame processing error:', e);
        setError(e instanceof Error ? e.message : 'Frame işleme hatası');
      }
    };

    intervalRef.current = setInterval(processAndSendFrame, 1000);
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isAnalyzing, cameraStarted]);

  // Component unmount olduğunda kamerayı durdur
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  const handleDownloadPDF = () => {
    // PDF generation logic (isteğe bağlı)
    alert('PDF generation is not implemented in this demo.');
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow bg-white pt-20 flex flex-col items-center justify-center">
        <div className="w-full max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col items-center justify-center">
          <div className="space-y-6 w-full flex flex-col items-center justify-center">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                Forensic Live Analysis
              </h1>
              <p className="text-xl text-gray-600">
                Real-time crime behavior detection through your camera
              </p>
            </div>

            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                <span className="block sm:inline">{error}</span>
              </div>
            )}

            <div className="flex flex-col items-center">
              <div className="mb-4 flex gap-4">
                <button
                  onClick={cameraStarted ? stopCamera : startCamera}
                  className={`px-6 py-2 rounded-lg font-bold transition-colors ${
                    cameraStarted ? 'bg-gray-500 hover:bg-gray-700' : 'bg-green-600 hover:bg-green-700'
                  } text-white`}
                  disabled={isAnalyzing}
                >
                  {cameraStarted ? 'Stop Camera' : 'Start Camera'}
                </button>
                <button
                  onClick={() => setIsAnalyzing(!isAnalyzing)}
                  className={`px-6 py-2 rounded-lg font-bold transition-colors ${
                    isAnalyzing ? 'bg-red-600 hover:bg-red-700' : 'bg-orange-500 hover:bg-orange-600'
                  } text-white`}
                  disabled={!cameraStarted}
                >
                  {isAnalyzing ? 'Stop Analysis' : 'Start Analysis'}
                </button>
              </div>

              <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden mb-4 w-full max-w-xl flex items-center justify-center relative">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover"
                  style={{ background: '#000', minHeight: 320 }}
                />
                <canvas
                  ref={canvasRef}
                  className="absolute inset-0 w-full h-full pointer-events-none"
                  style={{ zIndex: 10 }}
                />
                {!cameraStarted && (
                  <div className="absolute inset-0 flex items-center justify-center bg-gray-800 bg-opacity-50 text-white z-20">
                    <p>Camera is not active</p>
                  </div>
                )}
              </div>
            </div>

            <div className="flex justify-center w-full">
              <ForensicAnalysisResults
                results={frameResults}
                isAnalyzing={isAnalyzing}
              />
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
} 

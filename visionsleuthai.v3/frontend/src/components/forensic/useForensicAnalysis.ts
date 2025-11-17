import { useEffect, useRef, useState } from 'react';
import * as cocoSsd from '@tensorflow-models/coco-ssd';
import * as tf from '@tensorflow/tfjs';
import '@tensorflow/tfjs-backend-webgl';

export type Detection = {
  type: string;
  confidence: number;
  bbox: [number, number, number, number];
};

export const useForensicAnalysis = (videoRef: React.RefObject<HTMLVideoElement>) => {
  const [results, setResults] = useState<Detection[]>([]);
  const [model, setModel] = useState<cocoSsd.ObjectDetection | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const animationRef = useRef<number>();

  // Modeli yükle
  useEffect(() => {
    let isMounted = true;
    async function loadModel() {
      await tf.setBackend('webgl');
      await tf.ready();
      const loadedModel = await cocoSsd.load();
      if (isMounted) setModel(loadedModel);
    }
    loadModel();
    return () => {
      isMounted = false;
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  // Analiz döngüsü
  const analyzeFrame = async () => {
    if (!videoRef.current || !model || !isAnalyzing) return;
    const predictions = await model.detect(videoRef.current);
    const detections: Detection[] = predictions.map(pred => ({
      type: pred.class,
      confidence: pred.score ?? 0,
      bbox: pred.bbox as [number, number, number, number],
    }));
    setResults(prev => [
      ...detections,
      ...prev.slice(0, 50 - detections.length),
    ]);
    animationRef.current = requestAnimationFrame(analyzeFrame);
  };

  useEffect(() => {
    if (isAnalyzing) {
      animationRef.current = requestAnimationFrame(analyzeFrame);
    } else if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAnalyzing, model]);

  return { results, isAnalyzing, setIsAnalyzing };
}; 
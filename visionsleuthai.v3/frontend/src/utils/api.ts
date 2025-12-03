export interface Detection {
  type: string;
  confidence: number;
}

export interface Frame {
  frameNumber: number;
  timestamp: string;
  detections: Detection[];
  riskScore: number;
  contextualFactors: string[];
}

export interface CrimeDistribution {
  type: string;
  count: number;
  percentage: string;
}

export interface Recommendations {
  immediateActions: string[];
  longTermSuggestions: string[];
}

export interface AnalysisResult {
  id: string;
  status: string;
  timestamp: string;
  video_path: string;
  results_path: string | null;
  error: string | null;
  processingDate: string;
  modelVersion: string;
  progress?: number;
  processed_frames?: number;
  total_frames?: number;
  summary: {
    duration: number;
    totalFrames: number;
    processedFrames: number;
    videoSize: number;
    format: string;
    riskAssessment?: {
      overallRisk: {
        level: string;
        score: number;
        confidenceInterval: string;
      };
    };
    crimeDistribution?: CrimeDistribution[];
    recommendations?: Recommendations;
  };
  frames?: Frame[];
  academic_metrics?: {
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
    confusion_matrix: number[][];
    detection_metrics: {
      true_positives: number;
      false_positives: number;
      false_negatives: number;
    };
  };
  model_performance?: {
    inference_time: number;
    frames_processed: number;
    average_confidence: number;
    model_version?: string;
    processing_efficiency?: number;
  };
  forensic_metadata?: {
    case_id: string;
    evidence_hash: string;
    chain_of_custody: string;
    analysis_date: string;
    analyst: string;
    verification_status: string;
  };
  forensic_analysis?: {
    dangerous_objects_detected: number;
    high_risk_frames: number;
    evidence_quality: string;
    legal_compliance: {
      privacy_protection: string;
      data_integrity: string;
      chain_of_custody: string;
    };
  };
}

// Environment variables with type safety
declare global {
  interface Window {
    env: {
      NEXT_PUBLIC_API_URL?: string;
      NEXT_PUBLIC_WS_URL?: string;
    }
  }
}

const getApiBaseUrl = (): string => {
  // Next.js environment variables are available at build time
  const defaultUrl = 'https://masterthesis-zk81.onrender.com';
  const envUrl = process.env.NEXT_PUBLIC_API_URL || defaultUrl;
  return envUrl.replace(/\/+$/, '');
};

const getWsBase = (): string => {
  // Prefer explicit WS env, else derive from API base
  const fromEnv = process.env.NEXT_PUBLIC_WS_URL || '';
  if (fromEnv) return fromEnv.replace(/\/+$/, '');
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://masterthesis-zk81.onrender.com';
  // Convert http(s) -> ws(s)
  return apiUrl.replace(/\/+$/, '').replace(/^http:/, 'ws:').replace(/^https:/, 'wss:');
};

const API_BASE_URL = getApiBaseUrl();

export const uploadVideo = async (file: File): Promise<AnalysisResult> => {
  try {
    const formData = new FormData();
    // Backend expects the field name 'video'
    formData.append('video', file);

    const uploadUrl = `${API_BASE_URL}/api/video/upload`;

    const response = await fetch(uploadUrl, {
      method: 'POST',
      body: formData,
      signal: AbortSignal.timeout(300000),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Upload failed with status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Upload error:', error);
    throw error;
  }
};

export const getAnalysisResults = async (videoId: string): Promise<AnalysisResult> => {
  try {
    console.log(`Fetching analysis results for video ID: ${videoId}`);
    console.log(`API URL: ${API_BASE_URL}/api/video/analysis/${videoId}`);
    
    const response = await fetch(`${API_BASE_URL}/api/video/analysis/${videoId}`);
    
    console.log(`Response status: ${response.status}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error('API Error:', errorData);
      throw new Error(errorData.detail || 'Failed to get analysis results');
    }

    const result = await response.json();
    console.log('Analysis result:', result);
    return result;
  } catch (error) {
    console.error('Analysis results error:', error);
    throw error;
  }
};

export function connectToWebSocket(
  clientId: string,
  onMessage: (result: AnalysisResult) => void,
  onError: (error: Error) => void
): WebSocket {
  const wsBase = getWsBase();
  const wsUrl = `${wsBase}/api/live/feed/${encodeURIComponent(clientId)}`;
  const ws = new WebSocket(wsUrl);
  
  ws.onmessage = (event) => {
    try {
      const result = JSON.parse(event.data) as AnalysisResult;
      onMessage(result);
    } catch (error) {
      onError(error instanceof Error ? error : new Error('Failed to parse WebSocket message'));
    }
  };
  
  ws.onerror = (error) => {
    onError(error instanceof Error ? error : new Error('WebSocket error occurred'));
  };
  
  return ws;
}

export async function startLiveAnalysis(): Promise<void> {
  try {
    const response = await fetch('/api/live-analysis/start', {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error('Failed to start live analysis');
    }
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Failed to start live analysis');
  }
}

/**
 * Send a frame to the backend for live analysis
 * 
 * ARCHITECTURE (Proxy Route - Recommended):
 * - Browser makes request to: /api/live/frame (same-origin, NO CORS issues)
 * - Next.js server forwards to: ${NEXT_PUBLIC_API_URL}/api/live/frame (server-to-server)
 * - This eliminates CORS issues completely since browser only talks to same-origin Next.js server
 * 
 * ALTERNATIVE (Direct Backend Call):
 * - If proxy route doesn't work, backend CORS is configured to allow requests from Vercel frontend
 * - Backend allows origin: https://master-thesis-nu.vercel.app
 * - Backend allows methods: GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD
 */
export const sendFrame = async (imageData: string) => {
  try {
    // Validate input
    if (!imageData || typeof imageData !== 'string') {
      throw new Error('Invalid image data provided');
    }

    // DIRECT BACKEND CALL - Backend CORS is already configured
    // Backend allows origin: https://master-thesis-nu.vercel.app
    // This bypasses the Next.js proxy route that was causing 404 errors
    const backendUrl = API_BASE_URL;
    const backendEndpoint = `${backendUrl}/api/live/frame`;

    // Debug log (will appear in browser console)
    console.log('[sendFrame] Calling backend directly:', backendEndpoint);

    // Call backend directly (CORS is configured on backend)
    const response = await fetch(backendEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image: imageData }),
      // Add timeout to prevent hanging requests
      signal: AbortSignal.timeout(30000), // 30 second timeout
    });

    // Handle non-OK responses with detailed error messages
    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        // If response is not JSON, create error from status
        errorData = {
          error: `Server returned ${response.status} ${response.statusText}`,
        };
      }
      
      // Provide user-friendly error messages based on status code
      if (response.status === 404) {
        throw new Error('API endpoint not found. The backend route may not be deployed.');
      } else if (response.status >= 500) {
        throw new Error(`Backend server error: ${errorData.error || errorData.detail || 'Please try again later.'}`);
      } else if (response.status >= 400) {
        throw new Error(`Request error: ${errorData.error || errorData.detail || 'Invalid request.'}`);
      } else {
        throw new Error(errorData.error || errorData.detail || 'Failed to process frame');
      }
    }

    // Parse and return successful response
    try {
      return await response.json();
    } catch (parseError) {
      throw new Error('Failed to parse backend response');
    }
  } catch (error) {
    // Re-throw with better error messages
    if (error instanceof Error) {
      // Check for timeout/abort errors
      if (error.name === 'AbortError' || error.message.includes('timeout')) {
        throw new Error('Request timeout. Backend may be slow or unavailable.');
      }
      // Check for network errors
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        throw new Error('Network error. Please check your internet connection.');
      }
      // Check for CORS errors
      if (error.message.includes('CORS') || error.message.includes('Access-Control')) {
        throw new Error('CORS error. Backend may not be configured correctly.');
      }
      // Re-throw with original message
      throw error;
    }
    // Unknown error
    throw new Error('Unknown error occurred while processing frame');
  }
};

export const getAcademicAnalysis = async (videoId: string): Promise<AnalysisResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/video/academic-analysis/${videoId}`, {
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get academic analysis results');
    }

    return response.json();
  } catch (error) {
    console.error('Academic analysis error:', error);
    throw error;
  }
};

export const getDetailedAnalysis = async (videoId: string): Promise<{
  academic_metrics: AnalysisResult['academic_metrics'];
  model_performance: AnalysisResult['model_performance'];
  detection_summary: {
    total_detections: number;
    detection_by_class: Record<string, number>;
    confidence_distribution: number[];
  };
}> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/video/detailed-analysis/${videoId}`, {
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get detailed analysis');
    }

    return response.json();
  } catch (error) {
    console.error('Detailed analysis error:', error);
    throw error;
  }
};

/**
 * Generate a professional forensic report from detection results
 * 
 * @param detections Array of detection objects with timestamp, type, confidence, bbox, etc.
 * @returns Professional forensic report text
 */
export const generateForensicReport = async (detections: Array<{
  type?: string;
  label?: string;
  class_name?: string;
  confidence: number;
  bbox: number[];
  risk_level?: string;
  risk_score?: number;
  timestamp?: string;
}>): Promise<string> => {
  try {
    // Normalize detections format
    const normalizedDetections = detections.map(det => ({
      type: det.type || det.label || det.class_name || 'unknown',
      confidence: det.confidence,
      bbox: det.bbox || [0, 0, 0, 0],
      risk_level: det.risk_level,
      risk_score: det.risk_score,
    }));

    const detectionData = {
      timestamp: new Date().toISOString(),
      detections: normalizedDetections
    };

    const response = await fetch(`${API_BASE_URL}/api/forensic/generate-report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(detectionData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to generate forensic report');
    }

    const result = await response.json();
    return result.report;
  } catch (error) {
    console.error('Forensic report generation error:', error);
    throw error;
  }
}; 

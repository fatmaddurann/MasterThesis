import React, { useEffect, useRef, useState } from 'react';
import jsPDF from 'jspdf';
import { generateForensicReport } from '@/utils/api';

interface Detection {
  type: string;
  confidence: number;
  x: number;
  y: number;
}

interface AnalysisResult {
  timestamp: string;
  detections: Detection[];
}

interface ForensicLiveAnalysisBoxProps {
  results: AnalysisResult[];
  isAnalyzing: boolean;
  cameraStarted: boolean;
  error?: string | null;
  onDownloadPDF: () => void;
  status: string;
}

const getRiskLevel = (confidence: number) => {
  if (confidence > 85) return 'High Risk';
  if (confidence > 70) return 'Medium Risk';
  return 'Low Risk';
};
const getRiskClass = (confidence: number) => {
  if (confidence > 85) return 'high';
  if (confidence > 70) return 'medium';
  return 'low';
};

export default function ForensicLiveAnalysisBox({ results, isAnalyzing, cameraStarted, error, onDownloadPDF, status }: ForensicLiveAnalysisBoxProps) {
  const resultsBoxRef = useRef<HTMLDivElement>(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);

  useEffect(() => {
    if (resultsBoxRef.current) {
      resultsBoxRef.current.scrollTop = 0;
    }
  }, [results]);

  // Advanced forensic report handler
  const handleDownloadAdvancedReport = async () => {
    if (results.length === 0) return;
    
    setIsGeneratingReport(true);
    try {
      // Flatten results to get all detections with timestamps
      const allDetections = results.flatMap(result => 
        result.detections.map(det => ({
          type: det.type,
          confidence: det.confidence / 100, // Convert percentage to decimal if needed
          bbox: [det.x, det.y, det.x + 50, det.y + 50], // Approximate bbox from x,y
          timestamp: result.timestamp,
        }))
      );

      // Generate professional forensic report from backend
      const reportText = await generateForensicReport(allDetections);
      
      // Create PDF from the report text
      const doc = new jsPDF();
      doc.setFontSize(16);
      doc.text('Forensic Live Analysis Report', 105, 20, { align: 'center' });
      doc.setFontSize(10);
      
      // Split report into pages
      const lines = doc.splitTextToSize(reportText, 180);
      let y = 35;
      const pageHeight = 270;
      const lineHeight = 7;
      
      lines.forEach((line: string) => {
        if (y > pageHeight) {
          doc.addPage();
          y = 20;
        }
        doc.text(line, 14, y);
        y += lineHeight;
      });
      
      doc.save('forensic-live-analysis-report.pdf');
    } catch (error) {
      console.error('Error generating advanced report:', error);
      alert('Failed to generate forensic report. Please try again.');
    } finally {
      setIsGeneratingReport(false);
    }
  };

  return (
    <div className="analysis-container w-full max-w-2xl mt-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <span>Live Analysis Results</span>
        </h2>
        <button
          onClick={onDownloadPDF || handleDownloadAdvancedReport}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
          disabled={results.length === 0 || isGeneratingReport}
        >
          {isGeneratingReport ? 'Generating Report...' : 'Download PDF Report'}
        </button>
      </div>
      <div className="status-indicator mb-2">
        <div className={`pulse-dot ${isAnalyzing ? 'status-analyzing' : cameraStarted ? 'status-active' : 'status-ready'}`}></div>
        <span id="analysis-status">{status}</span>
      </div>
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded border border-red-300 text-center">
          <strong>Error:</strong> {error}
        </div>
      )}
      <div ref={resultsBoxRef} className="results-box">
        {results.length === 0 ? (
          <div className="empty-state">
            <p>Analysis will appear here when started</p>
          </div>
        ) : (
          results.map((res, idx) => (
            <div key={idx} className="analysis-result">
              <div className="timestamp">{res.timestamp}</div>
              {res.detections.map((detection, dIdx) => (
                <div key={dIdx}>
                  <div className="detection">
                    <span className="object-type">{detection.type}</span>
                    <span className="confidence">{detection.confidence}% confidence</span>
                    <span className={`risk-level ${getRiskClass(Number(detection.confidence))}`}>{getRiskLevel(Number(detection.confidence))}</span>
                  </div>
                  <div className="coordinates">Position: ({detection.x}, {detection.y})</div>
                </div>
              ))}
            </div>
          ))
        )}
      </div>
      <style jsx>{`
        .analysis-container {
          background: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          margin-bottom: 20px;
        }
        .status-indicator {
          display: flex;
          align-items: center;
          margin: 10px 0;
          font-weight: bold;
        }
        .pulse-dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          margin-right: 8px;
          background: #9E9E9E;
        }
        .status-ready .pulse-dot { background: #9E9E9E; }
        .status-active .pulse-dot { background: #4CAF50; animation: pulse 2s infinite; }
        .status-analyzing .pulse-dot { background: #FF9800; animation: pulse 1s infinite; }
        @keyframes pulse {
          0% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.3); opacity: 0.7; }
          100% { transform: scale(1); opacity: 1; }
        }
        .results-box {
          max-height: 400px;
          overflow-y: auto;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          padding: 10px;
          background: #f9f9f9;
        }
        .empty-state {
          color: #757575;
          text-align: center;
          padding: 20px;
        }
        .analysis-result {
          background: white;
          border-left: 4px solid #2196F3;
          padding: 12px;
          margin-bottom: 10px;
          border-radius: 0 4px 4px 0;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .timestamp {
          color: #616161;
          font-size: 0.85em;
          margin-bottom: 5px;
        }
        .detection {
          display: flex;
          gap: 15px;
          margin: 8px 0;
          flex-wrap: wrap;
        }
        .object-type { 
          font-weight: bold; 
          color: #1e3a8a; /* Koyu lacivert - okunabilir */
        }
        .confidence { color: #757575; }
        .risk-level { font-weight: bold; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; }
        .risk-level.high { background: #FFEBEE; color: #C62828; }
        .risk-level.medium { background: #FFF8E1; color: #F57F17; }
        .risk-level.low { background: #E8F5E9; color: #2E7D32; }
        .coordinates { color: #2196F3; font-size: 0.85em; }
      `}</style>
    </div>
  );
} 
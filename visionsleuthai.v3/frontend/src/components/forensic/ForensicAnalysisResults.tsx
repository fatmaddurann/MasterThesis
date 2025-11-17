import React, { useEffect, useState } from 'react';
import { Detection } from './useForensicAnalysis';
import jsPDF from 'jspdf';
import { generateForensicReport } from '@/utils/api';

interface ForensicAnalysisResultsProps {
  results: DetectionWithTimestamp[];
  isAnalyzing: boolean;
  onDownloadPDF?: () => void;
}

// Detection tipini timestamp ile genişlet
export type DetectionWithTimestamp = Detection & { 
  timestamp: string;
  risk: 'High' | 'Medium' | 'Low';
};

function getRiskColor(risk: 'High' | 'Medium' | 'Low') {
  switch (risk) {
    case 'High':
      return 'text-red-700';
    case 'Medium':
      return 'text-orange-700';
    default:
      return 'text-indigo-900'; // Koyu lacivert - sarı arka plan üzerinde okunabilir
  }
}

function getRiskBackground(risk: 'High' | 'Medium' | 'Low') {
  switch (risk) {
    case 'High':
      return 'bg-red-100';
    case 'Medium':
      return 'bg-orange-100';
    default:
      return 'bg-yellow-100';
  }
}

function getAcademicExplanation(type: string, conf: number, risk: 'High' | 'Medium' | 'Low') {
  const confidence = Math.round(conf * 100);
  const riskLevel = risk.toLowerCase();
  return `Detection of ${type} with ${confidence}% confidence. Risk level: ${riskLevel}.`;
}

export const ForensicAnalysisResults: React.FC<ForensicAnalysisResultsProps> = ({
  results,
  isAnalyzing,
  onDownloadPDF,
}) => {
  const [latestResults, setLatestResults] = useState<DetectionWithTimestamp[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isGeneratingAdvancedReport, setIsGeneratingAdvancedReport] = useState(false);

  // Son 10 sonucu güncelle
  useEffect(() => {
    if (!isInitialized && results.length > 0) {
      setIsInitialized(true);
    }
    setLatestResults(results.slice(0, 10));
  }, [results, isInitialized]);

  // Bar chart data
  const freq: Record<string, number> = {};
  results.forEach(r => {
    freq[r.type] = (freq[r.type] || 0) + 1;
  });
  const types = Object.keys(freq);

  // Hotspot for bbox centers
  const hotspots = results.map(r => ({
    x: r.bbox[0] + (r.bbox[2] - r.bbox[0]) / 2,
    y: r.bbox[1] + (r.bbox[3] - r.bbox[1]) / 2,
    type: r.type,
    conf: r.confidence,
    risk: r.risk,
  }));

  // Advanced forensic report (using backend generator)
  const handleDownloadAdvancedReport = async () => {
    if (results.length === 0) return;
    
    setIsGeneratingAdvancedReport(true);
    try {
      // Prepare detection data for backend
      const detectionData = results.map(r => ({
        type: r.type,
        confidence: r.confidence,
        bbox: r.bbox,
        risk_level: r.risk,
        timestamp: r.timestamp,
      }));

      // Generate professional forensic report from backend
      const reportText = await generateForensicReport(detectionData);
      
      // Create PDF from the report text
      const doc = new jsPDF();
      doc.setFontSize(16);
      doc.text('Forensic Analysis Report', 105, 20, { align: 'center' });
      doc.setFontSize(10);
      
      // Split report into pages (jsPDF has a text wrapping limit)
      const lines = doc.splitTextToSize(reportText, 180); // 180mm width
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
      
      doc.save('forensic-analysis-report.pdf');
    } catch (error) {
      console.error('Error generating advanced report:', error);
      alert('Failed to generate forensic report. Please try again.');
    } finally {
      setIsGeneratingAdvancedReport(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-4 w-full max-w-4xl">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Forensic Analysis Results</h2>
        <button
          onClick={onDownloadPDF || handleDownloadAdvancedReport}
          disabled={results.length === 0 || isGeneratingAdvancedReport}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded disabled:opacity-50"
          title="Professional forensic report with all sections"
        >
          {isGeneratingAdvancedReport ? 'Generating Report...' : 'Download PDF Report'}
        </button>
      </div>

      {/* Event Timeline */}
      <div className="mb-6">
        <h3 className="font-medium mb-2">Event Timeline</h3>
        <div className="max-h-96 overflow-y-auto">
          <ul className="divide-y">
            {!isInitialized ? (
              <li className="p-3 text-gray-500">Waiting for camera...</li>
            ) : latestResults.length === 0 ? (
              <li className="p-3 text-gray-500">{isAnalyzing ? 'Analyzing...' : 'No detections yet.'}</li>
            ) : (
              latestResults.map((r, i) => (
                <li key={i} className={`p-3 ${getRiskBackground(r.risk)}`}>
                  <div className="flex justify-between">
                    <span className="font-medium text-indigo-900">{r.type}</span>
                    <span className={`text-xs font-semibold ${getRiskColor(r.risk)}`}>
                      {r.risk} risk level
                    </span>
                  </div>
                  <div className="text-xs text-gray-500">Confidence: {Math.round(r.confidence * 100)}%</div>
                  <div className="text-xs text-gray-500">Timestamp: {r.timestamp}</div>
                  <div className="text-xs text-blue-700 mt-1">
                    {getAcademicExplanation(r.type, r.confidence, r.risk)}
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>
      </div>

      {/* Bar Chart */}
      {types.length > 0 && (
        <div className="mb-6">
          <h3 className="font-medium mb-2">Detection Frequency</h3>
          <div className="h-32 bg-gray-50 rounded p-2 flex items-end gap-2">
            {types.map((type) => (
              <div key={type} className="flex-1 flex flex-col items-center">
                <div
                  className="w-6 rounded-t"
                  style={{
                    height: `${Math.min(freq[type] * 20, 100)}%`,
                    background: '#2563eb',
                  }}
                  title={`${type}: ${freq[type]} times`}
                ></div>
                <span className="text-xs mt-1 text-gray-700">{type}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hotspot Map */}
      {hotspots.length > 0 && (
        <div className="mb-6">
          <h3 className="font-medium mb-2">Hotspot Map</h3>
          <div className="relative w-full h-40 bg-gray-100 rounded">
            {hotspots.map((h, i) => (
              <div
                key={i}
                className="absolute rounded-full border-2"
                style={{
                  left: `${Math.min(Math.max(h.x / 640 * 100, 0), 100)}%`,
                  top: `${Math.min(Math.max(h.y / 480 * 100, 0), 100)}%`,
                  width: 12,
                  height: 12,
                  background: h.risk === 'High' ? '#ef4444' : h.risk === 'Medium' ? '#f59e0b' : '#10b981',
                  borderColor: h.risk === 'High' ? '#dc2626' : h.risk === 'Medium' ? '#d97706' : '#059669',
                  transform: 'translate(-50%, -50%)',
                }}
                title={`${h.type} (${Math.round(h.conf * 100)}%) - ${h.risk} risk`}
              ></div>
            ))}
          </div>
        </div>
      )}

      {/* Summary */}
      <div className="mt-6">
        <h3 className="font-medium mb-2">Summary</h3>
        <div className="text-gray-700 text-sm">
          <div className="grid grid-cols-2 gap-4">
            <div>
              Total detections: <b>{results.length}</b>
            </div>
            <div>
              High risk detections: <b className="text-red-600">
                {results.filter(r => r.risk === 'High').length}
              </b>
            </div>
            <div>
              Detected object types: {types.join(', ') || 'None'}
            </div>
            <div>
              Average confidence: {results.length > 0 
                ? `${Math.round(results.reduce((a, b) => a + b.confidence, 0) / results.length * 100)}%`
                : '-'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 
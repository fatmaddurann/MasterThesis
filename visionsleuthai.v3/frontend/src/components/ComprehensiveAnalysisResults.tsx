'use client';
// Comprehensive Analysis Results Component - Updated 2025-11-29

import React, { useState, useRef } from 'react';
import { 
  ShieldExclamationIcon, 
  ClockIcon, 
  ChartBarIcon, 
  EyeIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import html2pdf from 'html2pdf.js';

interface Detection {
  type: string;
  class_name: string;
  confidence: number;
  bbox: number[];
  risk_score: number;
  track_id: number;
  original_class?: string;
  risk_level?: string;
}

interface SuspiciousInteraction {
  type: string;
  count: number;
  max_risk: number;
}

interface FrameResult {
  detections: Detection[];
  suspicious_interactions: SuspiciousInteraction[];
  confidence: number;
}

interface ForensicMetadata {
  case_id: string;
  evidence_hash: string;
  chain_of_custody: string;
  analysis_date: string;
  analyst: string;
  verification_status: string;
}

interface Summary {
  duration: number;
  totalFrames: number;
  processedFrames: number;
  videoSize: number;
  format: string;
  resolution?: string;
  fps?: number;
}

interface ModelPerformance {
  inference_time: number;
  frames_processed: number;
  average_confidence: number;
  model_version: string;
  processing_efficiency: number;
}

interface ForensicAnalysis {
  dangerous_objects_detected: number;
  high_risk_frames: number;
  evidence_quality: string;
  legal_compliance: {
    privacy_protection: string;
    data_integrity: string;
    chain_of_custody: string;
  };
}

interface AnalysisData {
  id: string;
  status: string;
  timestamp: string;
  video_path: string;
  results_path: string | null;
  summary?: Summary;
  model_performance?: ModelPerformance;
  forensic_metadata?: ForensicMetadata;
  frames?: FrameResult[];
  forensic_analysis?: ForensicAnalysis;
}

interface ComprehensiveAnalysisResultsProps {
  analysisData?: AnalysisData;
}

export default function ComprehensiveAnalysisResults({ analysisData }: ComprehensiveAnalysisResultsProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'detections' | 'timeline' | 'risk' | 'forensic'>('overview');
  const reportRef = useRef<HTMLDivElement>(null);

  const downloadPDF = async () => {
    if (!reportRef.current) return;

    const element = reportRef.current;
    const opt = {
      margin: 1,
      filename: `forensic_report_${analysisData?.id || 'analysis'}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };

    try {
      await html2pdf().set(opt).from(element).save();
    } catch (error) {
      console.error('PDF generation failed:', error);
      alert('PDF oluşturulurken bir hata oluştu. Lütfen tekrar deneyin.');
    }
  };

  if (!analysisData) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
          <DocumentTextIcon className="w-8 h-8 text-gray-400" />
        </div>
        <p className="text-gray-500">No analysis data available</p>
      </div>
    );
  }

  // Calculate statistics
  const totalDetections = analysisData.frames?.reduce((sum, frame) => sum + frame.detections.length, 0) || 0;
  const dangerousDetections = analysisData.frames?.reduce((sum, frame) => 
    sum + frame.detections.filter(det => ['gun', 'knife', 'weapon'].includes(det.class_name)).length, 0
  ) || 0;
  const highRiskDetections = analysisData.frames?.reduce((sum, frame) => 
    sum + frame.detections.filter(det => det.risk_score >= 0.8).length, 0
  ) || 0;
  const avgConfidence = analysisData.model_performance?.average_confidence;
  const processingEfficiency = analysisData.model_performance?.processing_efficiency;

  // Get unique detections by type
  const detectionTypes = Array.from(new Set(analysisData.frames?.flatMap(frame => 
    frame.detections.map(det => det.class_name)
  ) || []));

  // Get timeline data
  const timelineData = analysisData.frames?.map((frame, index) => ({
    frameNumber: index + 1,
    timestamp: (index / (analysisData.summary?.fps || 30)).toFixed(2),
    detections: frame.detections,
    riskLevel: frame.detections.some(det => det.risk_score >= 0.8) ? 'High' : 
               frame.detections.some(det => det.risk_score >= 0.5) ? 'Medium' : 'Low'
  })) || [];

  const tabs = [
    { id: 'overview', name: 'Overview', icon: ChartBarIcon },
    { id: 'detections', name: 'Detections', icon: EyeIcon },
    { id: 'timeline', name: 'Timeline', icon: ClockIcon },
    { id: 'risk', name: 'Risk Analysis', icon: ShieldExclamationIcon },
    { id: 'forensic', name: 'Forensic Report', icon: DocumentTextIcon }
  ];

  return (
    <div ref={reportRef} className="bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <h2 className="text-xl font-semibold text-gray-800">Comprehensive Analysis Results</h2>
        <p className="text-sm text-gray-600 mt-1">
          Case ID: {analysisData.forensic_metadata?.case_id || analysisData.id} | 
          Analysis Date: {new Date(analysisData.forensic_metadata?.analysis_date || analysisData.timestamp).toLocaleString()}
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.name}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="flex items-center">
                  <EyeIcon className="w-8 h-8 text-blue-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-blue-600">Total Detections</p>
                    <p className="text-2xl font-bold text-blue-900">{totalDetections}</p>
                  </div>
                </div>
              </div>
              <div className="bg-red-50 rounded-lg p-4">
                <div className="flex items-center">
                  <ShieldExclamationIcon className="w-8 h-8 text-red-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-red-600">Dangerous Objects</p>
                    <p className="text-2xl font-bold text-red-900">{dangerousDetections}</p>
                  </div>
                </div>
              </div>
              <div className="bg-orange-50 rounded-lg p-4">
                <div className="flex items-center">
                  <ExclamationTriangleIcon className="w-8 h-8 text-orange-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-orange-600">High Risk Frames</p>
                    <p className="text-2xl font-bold text-orange-900">{highRiskDetections}</p>
                  </div>
                </div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="flex items-center">
                  <CheckCircleIcon className="w-8 h-8 text-green-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-green-600">Processing Efficiency</p>
                    <p className="text-2xl font-bold text-green-900">
                      {processingEfficiency !== undefined ? processingEfficiency.toFixed(1) : 'N/A'}%
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Video Information */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="text-lg font-medium text-blue-900 mb-3">Video Information</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-blue-700 font-medium">Duration</p>
                  <p className="font-semibold text-blue-900">{analysisData.summary?.duration?.toFixed(2) || 'N/A'}s</p>
                </div>
                <div>
                  <p className="text-blue-700 font-medium">Frames</p>
                  <p className="font-semibold text-blue-900">{analysisData.summary?.processedFrames || 0}/{analysisData.summary?.totalFrames || 0}</p>
                </div>
                <div>
                  <p className="text-blue-700 font-medium">Format</p>
                  <p className="font-semibold text-blue-900">{analysisData.summary?.format || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-blue-700 font-medium">Resolution</p>
                  <p className="font-semibold text-blue-900">{analysisData.summary?.resolution || 'N/A'}</p>
                </div>
              </div>
            </div>

            {/* Model Performance */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="text-lg font-medium text-green-900 mb-3">Model Performance</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-green-700 font-medium">Model Version</p>
                  <p className="font-semibold text-green-900">{analysisData.model_performance?.model_version || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-green-700 font-medium">Inference Time</p>
                  <p className="font-semibold text-green-900">{analysisData.model_performance?.inference_time?.toFixed(2) || 'N/A'}ms</p>
                </div>
                <div>
                  <p className="text-green-700 font-medium">Avg Confidence</p>
                  <p className="font-semibold text-green-900">
                    {avgConfidence !== undefined ? ((avgConfidence * 100).toFixed(1)) : 'N/A'}%
                  </p>
                </div>
                <div>
                  <p className="text-green-700 font-medium">Evidence Quality</p>
                  <p className="font-semibold text-green-900">{analysisData.forensic_analysis?.evidence_quality || 'N/A'}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'detections' && (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-800">Detection Results</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {detectionTypes.map((type) => {
                const typeDetections = analysisData.frames?.flatMap(frame => 
                  frame.detections.filter(det => det.class_name === type)
                ) || [];
                const avgConfidence = typeDetections.length > 0 ? typeDetections.reduce((sum, det) => sum + det.confidence, 0) / typeDetections.length : 0;
                const isDangerous = ['gun', 'knife', 'weapon'].includes(type);
                
                return (
                  <div key={type} className={`rounded-lg p-4 border-2 ${
                    isDangerous ? 'border-red-300 bg-red-100' : 'border-blue-300 bg-blue-100'
                  }`}>
                    <div className="flex items-center justify-between">
                      <h4 className={`font-medium ${isDangerous ? 'text-red-900' : 'text-blue-900'}`}>
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                      </h4>
                      {isDangerous && <ExclamationTriangleIcon className="w-5 h-5 text-red-800" />}
                    </div>
                    <p className={`text-sm mt-1 ${isDangerous ? 'text-red-800' : 'text-blue-800'}`}>
                      Count: {typeDetections.length}
                    </p>
                    <p className={`text-sm ${isDangerous ? 'text-red-800' : 'text-blue-800'}`}>
                      Avg Confidence: {(avgConfidence * 100).toFixed(1)}%
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {activeTab === 'timeline' && (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-800">Timeline Analysis</h3>
            <div className="max-h-96 overflow-y-auto bg-white border border-gray-200 rounded-lg p-4">
              {timelineData.filter(frame => frame.detections.length > 0).map((frame) => (
                <div key={frame.frameNumber} className="border-l-4 border-blue-400 pl-4 py-3 mb-3 bg-blue-50 rounded-r-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-blue-900">
                        Frame {frame.frameNumber} - {frame.timestamp}s
                      </p>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {frame.detections.map((detection, idx) => (
                          <span
                            key={idx}
                            className={`px-3 py-1 rounded-full text-xs font-medium ${
                              detection.risk_score >= 0.8 
                                ? 'bg-red-200 text-red-900'
                                : detection.risk_score >= 0.5
                                ? 'bg-orange-200 text-orange-900'
                                : 'bg-green-200 text-green-900'
                            }`}
                          >
                            {detection.class_name} ({(detection.confidence * 100).toFixed(1)}%)
                          </span>
                        ))}
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      frame.riskLevel === 'High' 
                        ? 'bg-red-200 text-red-900'
                        : frame.riskLevel === 'Medium'
                        ? 'bg-orange-200 text-orange-900'
                        : 'bg-green-200 text-green-900'
                    }`}>
                      {frame.riskLevel} Risk
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'risk' && (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-800">Risk Analysis</h3>
            
            {/* Risk Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-red-100 border border-red-300 rounded-lg p-4">
                <h4 className="font-semibold text-red-900 mb-2">High Risk Events</h4>
                <p className="text-2xl font-bold text-red-900">{analysisData.forensic_analysis?.high_risk_frames || 0}</p>
                <p className="text-sm text-red-800">Frames with risk score ≥ 0.8</p>
              </div>
              <div className="bg-orange-100 border border-orange-300 rounded-lg p-4">
                <h4 className="font-semibold text-orange-900 mb-2">Dangerous Objects</h4>
                <p className="text-2xl font-bold text-orange-900">{analysisData.forensic_analysis?.dangerous_objects_detected || 0}</p>
                <p className="text-sm text-orange-800">Guns, knives, weapons</p>
              </div>
              <div className="bg-green-100 border border-green-300 rounded-lg p-4">
                <h4 className="font-semibold text-green-900 mb-2">Evidence Quality</h4>
                <p className="text-2xl font-bold text-green-900">{analysisData.forensic_analysis?.evidence_quality || 'N/A'}</p>
                <p className="text-sm text-green-800">Processing quality</p>
              </div>
            </div>

            {/* Legal Compliance */}
            <div className="bg-blue-100 border border-blue-300 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-3">Legal Compliance</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center">
                  <CheckCircleIcon className="w-5 h-5 text-green-700 mr-2" />
                  <span className="text-sm text-blue-900 font-medium">
                    Privacy Protection: {analysisData.forensic_analysis?.legal_compliance?.privacy_protection || 'N/A'}
                  </span>
                </div>
                <div className="flex items-center">
                  <CheckCircleIcon className="w-5 h-5 text-green-700 mr-2" />
                  <span className="text-sm text-blue-900 font-medium">
                    Data Integrity: {analysisData.forensic_analysis?.legal_compliance?.data_integrity || 'N/A'}
                  </span>
                </div>
                <div className="flex items-center">
                  <CheckCircleIcon className="w-5 h-5 text-green-700 mr-2" />
                  <span className="text-sm text-blue-900 font-medium">
                    Chain of Custody: {analysisData.forensic_analysis?.legal_compliance?.chain_of_custody || 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'forensic' && (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-800">Forensic Report</h3>
            
            {/* Case Information */}
            <div className="bg-purple-100 border border-purple-300 rounded-lg p-4">
              <h4 className="font-semibold text-purple-900 mb-3">Case Information</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-purple-700 font-medium">Case ID</p>
                  <p className="font-semibold font-mono text-purple-900">{analysisData.forensic_metadata?.case_id || analysisData.id}</p>
                </div>
                <div>
                  <p className="text-purple-700 font-medium">Evidence Hash</p>
                  <p className="font-semibold font-mono text-purple-900">{analysisData.forensic_metadata?.evidence_hash || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-purple-700 font-medium">Analysis Date</p>
                  <p className="font-semibold text-purple-900">{new Date(analysisData.forensic_metadata?.analysis_date || analysisData.timestamp).toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-purple-700 font-medium">Analyst</p>
                  <p className="font-semibold text-purple-900">{analysisData.forensic_metadata?.analyst || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-purple-700 font-medium">Chain of Custody</p>
                  <p className="font-semibold text-purple-900">{analysisData.forensic_metadata?.chain_of_custody || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-purple-700 font-medium">Verification Status</p>
                  <p className="font-semibold text-purple-900">{analysisData.forensic_metadata?.verification_status || 'N/A'}</p>
                </div>
              </div>
            </div>

            {/* Analysis Summary */}
            <div className="bg-indigo-100 border border-indigo-300 rounded-lg p-4">
              <h4 className="font-semibold text-indigo-900 mb-3">Analysis Summary</h4>
              <div className="prose prose-sm max-w-none">
                <p className="text-indigo-900 font-medium">
                  This forensic analysis was conducted using {analysisData.model_performance?.model_version || 'N/A'} 
                  on a {analysisData.summary?.duration?.toFixed(2) || 'N/A'}-second video containing {analysisData.summary?.totalFrames || 0} frames. 
                  The analysis detected {totalDetections} total objects, including {dangerousDetections} dangerous objects 
                  and {analysisData.forensic_analysis?.high_risk_frames || 0} high-risk frames. The evidence quality is rated as 
                  {analysisData.forensic_analysis?.evidence_quality || 'N/A'} with a processing efficiency of 
                 {analysisData.model_performance?.processing_efficiency?.toFixed(1) || 'N/A'}%.
                </p>
              </div>
            </div>

            {/* Download Report Button */}
            <div className="flex justify-end">
              <button
                onClick={downloadPDF}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
              >
                <DocumentTextIcon className="w-4 h-4" />
                <span>Download Forensic Report</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

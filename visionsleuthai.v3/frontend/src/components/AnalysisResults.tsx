'use client';

import React from 'react';

interface Detection {
  class: string;
  confidence: number;
  bbox: number[];
}

interface SuspiciousInteraction {
  type: string;
  distance: number;
}

interface FrameResult {
  timestamp: string;
  frame_number: number;
  detections: Detection[];
  suspicious_interactions: SuspiciousInteraction[];
}

interface DetectionResult {
  id: string;
  timestamp: string;
  type: string;
  confidence: number;
  location: string;
}

export interface AnalysisResultsProps {
  results?: DetectionResult[];
}

export function AnalysisResults({ results = [] }: AnalysisResultsProps) {
  if (results.length === 0) {
    return (
      <div className="bg-black/20 backdrop-blur-sm rounded-lg p-8 text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-blue-500/20 flex items-center justify-center">
          <svg className="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <p className="text-gray-400">No detection results available yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {results.map((result) => (
        <div
          key={result.id}
          className="bg-black/20 backdrop-blur-sm rounded-lg p-4 border border-white/5"
        >
          <div className="flex items-start justify-between">
            <div>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-500/20 text-blue-400">
                {result.type}
              </span>
              <p className="mt-1 text-sm text-gray-300">{result.location}</p>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-gray-400">{result.timestamp}</p>
              <p className="mt-1 text-sm text-blue-400">
                {Math.round(result.confidence * 100)}% confidence
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
} 
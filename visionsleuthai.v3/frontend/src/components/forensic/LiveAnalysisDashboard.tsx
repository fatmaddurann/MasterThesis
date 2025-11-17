import React from 'react';

interface LiveAnalysisDashboardProps {
  report: {
    risk_score: number;
    detections: Array<{
      type: string;
      confidence: number;
      bbox: [number, number, number, number];
    }>;
  };
}

export default function LiveAnalysisDashboard({ report }: LiveAnalysisDashboardProps) {
  // Risk skoruna göre renk belirleme
  const getRiskColor = (score: number) => {
    if (score < 0.3) return 'bg-green-500';
    if (score < 0.7) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-4">
      <h2 className="text-xl font-bold mb-4">Live Analysis</h2>
      
      {/* Risk Score */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <h3 className="font-semibold">Risk Level</h3>
          <span className="text-sm font-mono">{Math.round(report.risk_score * 100)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div 
            className={`h-2.5 rounded-full transition-all duration-300 ${getRiskColor(report.risk_score)}`}
            style={{ width: `${report.risk_score * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Detections */}
      <div>
        <h3 className="font-semibold mb-2">Detected Objects</h3>
        {report.detections.length > 0 ? (
          <div className="space-y-2">
            {report.detections.map((detection, index) => (
              <div 
                key={index}
                className="flex items-center justify-between p-2 bg-gray-50 rounded"
              >
                <div>
                  <span className="font-medium">{detection.type}</span>
                  <span className="text-sm text-gray-500 ml-2">
                    ({detection.bbox[0]}, {detection.bbox[1]})
                  </span>
                </div>
                <span className="text-sm font-mono">
                  {Math.round(detection.confidence * 100)}%
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No dangerous objects detected</p>
        )}
      </div>

      {/* Status */}
      <div className="mt-4 text-sm text-gray-500">
        <p>Analysis is running in real-time</p>
        <p>Detecting: weapons, knives, guns, bombs</p>
      </div>
    </div>
  );
} 
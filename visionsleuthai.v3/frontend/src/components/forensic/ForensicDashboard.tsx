import React from 'react';
import { AnalysisResult, Frame, Detection, CrimeDistribution } from '@/utils/api';

interface ForensicDashboardProps {
  report: AnalysisResult;
}

const ForensicDashboard: React.FC<ForensicDashboardProps> = ({ report }) => {
  const handleDownloadPDF = async () => {
    if (typeof window !== 'undefined') {
      const html2pdf = (await import('html2pdf.js')).default;
      const element = document.getElementById('forensic-report-pdf');
      const button = document.getElementById('download-pdf-btn');
      if (button) button.style.display = 'none';
      if (element) {
        html2pdf().from(element).set({
          margin: 0.5,
          filename: 'forensic_report.pdf',
          html2canvas: { scale: 2 },
          jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
        }).save().then(() => {
          if (button) button.style.display = '';
        });
      }
    }
  };

  return (
    <div className="forensic-dashboard space-y-8 bg-white text-black" id="forensic-report-pdf" style={{ color: '#111', background: '#fff' }}>
      <div className="flex justify-end">
        <button id="download-pdf-btn" onClick={handleDownloadPDF} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Download PDF</button>
      </div>

      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Forensic Analysis Report</h2>
        <p className="text-sm text-gray-500">Analysis ID: {report.id}</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div>
          <p className="text-sm text-gray-500">Duration</p>
          <p className="text-gray-800">{report.summary.duration.toFixed(2)}s</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Resolution</p>
          <p className="text-gray-800">{report.summary.format}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Total Frames</p>
          <p className="text-gray-800">{report.summary.totalFrames}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Processed Frames</p>
          <p className="text-gray-800">{report.summary.processedFrames}</p>
        </div>
      </div>

      {report.academic_metrics && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">Detection Metrics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Accuracy</p>
              <p className="text-lg font-semibold">
                {(report.academic_metrics.accuracy * 100).toFixed(1)}%
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Precision</p>
              <p className="text-lg font-semibold">
                {(report.academic_metrics.precision * 100).toFixed(1)}%
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Recall</p>
              <p className="text-lg font-semibold">
                {(report.academic_metrics.recall * 100).toFixed(1)}%
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">F1 Score</p>
              <p className="text-lg font-semibold">
                {(report.academic_metrics.f1_score * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {report.model_performance && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Model Performance</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Inference Time</p>
              <p className="text-lg font-semibold">
                {report.model_performance.inference_time.toFixed(2)}ms
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Frames Processed</p>
              <p className="text-lg font-semibold">
                {report.model_performance.frames_processed}
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Average Confidence</p>
              <p className="text-lg font-semibold">
                {(report.model_performance.average_confidence * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Frames Analysis */}
      {report.frames && report.frames.length > 0 && (
        <section className="frames-analysis bg-white p-4 rounded-lg border border-gray-300">
          <h3 className="font-semibold mb-2">Frame Analysis</h3>
          <div className="space-y-4">
            {report.frames.map((frame: Frame, index: number) => (
              <div key={index} className="border border-gray-200 rounded-lg p-3">
                <div className="flex justify-between items-center mb-2">
                  <p className="text-sm font-medium text-gray-700">Frame {frame.frameNumber}</p>
                  <p className="text-sm text-gray-500">{frame.timestamp}</p>
                </div>
                <div className="space-y-2">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Detections:</p>
                    <ul className="list-disc list-inside text-sm text-gray-600">
                      {frame.detections.map((detection: Detection, dIndex: number) => (
                        <li key={dIndex}>
                          {detection.type} (Confidence: {detection.confidence.toFixed(2)})
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Risk Score:</p>
                    <p className="text-sm text-gray-600">{frame.riskScore.toFixed(2)}</p>
                  </div>
                  {frame.contextualFactors.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-gray-600">Contextual Factors:</p>
                      <ul className="list-disc list-inside text-sm text-gray-600">
                        {frame.contextualFactors.map((factor: string, fIndex: number) => (
                          <li key={fIndex}>{factor}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Summary */}
      <section className="summary bg-white p-4 rounded-lg border border-gray-300">
        <h3 className="font-semibold mb-2">Analysis Summary</h3>
        <div className="space-y-4">
          {report.summary.riskAssessment && (
            <div>
              <h4 className="text-sm font-medium text-gray-700">Risk Assessment</h4>
              <pre className="mt-1 text-sm text-gray-600 bg-gray-100 p-2 rounded">
                {JSON.stringify(report.summary.riskAssessment, null, 2)}
              </pre>
            </div>
          )}
          
          {report.summary.crimeDistribution && report.summary.crimeDistribution.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700">Crime Distribution</h4>
              <div className="mt-1 space-y-2">
                {report.summary.crimeDistribution.map((crime: CrimeDistribution, index: number) => (
                  <div key={index} className="flex justify-between text-sm">
                    <span>{crime.type}</span>
                    <span>{crime.count} ({crime.percentage})</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {report.summary.recommendations && (
            <div>
              <h4 className="text-sm font-medium text-gray-700">Recommendations</h4>
              <div className="mt-1 space-y-2">
                <div>
                  <p className="text-sm font-medium text-gray-600">Immediate Actions:</p>
                  <ul className="list-disc list-inside text-sm text-gray-600">
                    {report.summary.recommendations.immediateActions.map((action: string, index: number) => (
                      <li key={index}>{action}</li>
                    ))}
                  </ul>
                </div>
                {report.summary.recommendations.longTermSuggestions && (
                  <div>
                    <p className="text-sm font-medium text-gray-600">Long-term Suggestions:</p>
                    <ul className="list-disc list-inside text-sm text-gray-600">
                      {report.summary.recommendations.longTermSuggestions.map((suggestion: string, index: number) => (
                        <li key={index}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default ForensicDashboard; 

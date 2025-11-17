import React from 'react';
import './academic-report.css';
import type { AnalysisResult } from '@/utils/api';

export default function AcademicResults({ data }: { data: AnalysisResult }) {
  const { academic_metrics, summary } = data;

  return (
    <div className="academic-report">
      <section className="report-header">
        <h2>Forensic Video Analysis Report</h2>
        <div className="metadata-grid">
          <div>
            <span className="label">Analysis Date:</span>
            <span>{data.processingDate}</span>
          </div>
          <div>
            <span className="label">Model Version:</span>
            <span>{data.modelVersion}</span>
          </div>
        </div>
      </section>

      <section className="quantitative-section">
        <h3>Quantitative Analysis</h3>
        <div className="metrics-grid">
          <div className="metric-card">
            <h4>Precision</h4>
            <p>{academic_metrics?.precision ? (academic_metrics.precision * 100).toFixed(1) + '%' : '-'}</p>
            <small>TP/(TP+FP)</small>
          </div>
          <div className="metric-card">
            <h4>Recall</h4>
            <p>{academic_metrics?.recall ? (academic_metrics.recall * 100).toFixed(1) + '%' : '-'}</p>
            <small>TP/(TP+FN)</small>
          </div>
          <div className="metric-card">
            <h4>F1 Score</h4>
            <p>{academic_metrics?.f1_score ? (academic_metrics.f1_score * 100).toFixed(1) + '%' : '-'}</p>
            <small>2*P*R/(P+R)</small>
          </div>
          <div className="metric-card">
            <h4>True Positives</h4>
            <p>{academic_metrics?.detection_metrics.true_positives ?? '-'}</p>
          </div>
        </div>
      </section>

      <section className="temporal-analysis">
        <h3>Temporal Crime Distribution</h3>
        <table className="academic-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Event Type</th>
              <th>Confidence</th>
              <th>Contextual Factors</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan={4} className="text-center text-gray-400">No temporal pattern data</td>
            </tr>
          </tbody>
        </table>
      </section>

      {summary && (
        <>
          <section className="risk-assessment">
            <h3>Risk Assessment</h3>
            <div className="risk-indicator">
              <span className={`risk-level ${summary.riskAssessment?.overallRisk?.level?.toLowerCase() ?? ''}`}>
                {summary.riskAssessment?.overallRisk?.level ?? '-'}
              </span>
              <span>(Score: {summary.riskAssessment?.overallRisk?.score ?? '-'}/10)</span>
            </div>
            <div className="confidence-interval">
              Confidence Interval: {summary.riskAssessment?.overallRisk?.confidenceInterval ?? '-'}
            </div>
          </section>

          <section className="conclusions">
            <h3>Conclusions & Recommendations</h3>
            <div className="recommendations">
              <h4>Immediate Actions:</h4>
              <ul>
                {summary.recommendations?.immediateActions?.map((action: string, i: number) => (
                  <li key={i}>{action}</li>
                ))}
              </ul>
            </div>
            <div className="references">
              <h4>Methodological References:</h4>
              <p>1. YOLOv7: Trainable bag-of-freebies sets new state-of-the-art for real-time object detectors (2022)</p>
              <p>2. Temporal Analysis of Surveillance Footage: Best Practices in Forensic Video Analysis</p>
            </div>
          </section>
        </>
      )}
    </div>
  );
} 

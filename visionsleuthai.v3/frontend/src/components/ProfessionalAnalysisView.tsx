'use client';

import React from 'react';
import type { AnalysisResult } from '@/utils/api';
import AcademicResults from '@/components/AcademicResults';

interface ProfessionalAnalysisViewProps {
  results: AnalysisResult;
}

export default function ProfessionalAnalysisView({ results }: ProfessionalAnalysisViewProps) {
  return (
    <div>
      <h2 className="text-xl font-bold mb-2">Professional Analysis</h2>
      <pre className="bg-gray-100 p-4 rounded">{JSON.stringify(results, null, 2)}</pre>
      <AcademicResults data={results} />
    </div>
  );
} 
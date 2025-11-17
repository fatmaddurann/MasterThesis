'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import UploadCard from '@/components/UploadCard';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { AnalysisResult } from '@/utils/api';
import AcademicResults from '@/components/AcademicResults';
import ComprehensiveAnalysisResults from '@/components/ComprehensiveAnalysisResults';

const ProfessionalAnalysisView = dynamic(() => import('@/components/ProfessionalAnalysisView'), {
  loading: () => <div className="h-96 w-full bg-gray-100 animate-pulse rounded-lg" />
});

export default function VideoUploadPage() {
  const [analysisLevel, setAnalysisLevel] = useState<'basic' | 'advanced'>('basic');
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleUploadComplete = (results: AnalysisResult) => {
    setAnalysisResults(results);
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      
      <main className="flex-grow bg-gray-50 pt-20">
        <div className="container mx-auto px-4 py-6">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">Video Analysis</h1>
            <UploadCard onUploadComplete={handleUploadComplete} />
            
            {/* Comprehensive Analysis Results - Always visible when analysis is complete */}
            {analysisResults && (
              <ComprehensiveAnalysisResults analysisData={analysisResults as any} />
            )}

            {error && (
              <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-lg">
                {error}
              </div>
            )}
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
} 

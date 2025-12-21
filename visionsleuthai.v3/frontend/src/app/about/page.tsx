"use client";
import React from "react";
import { motion } from "framer-motion";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

export default function AboutPage() {
  const fadeInUp = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.5 }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-4xl mx-auto"
        >
          {/* Hero Section */}
          <div className="text-center mb-16">
            <h1 className="text-4xl font-bold text-gray-800 mb-4">
              About VisionSleuth AI
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Advanced AI-Powered Forensic Crime Detection System for Real-Time Video Analysis
            </p>
          </div>

          {/* Project Overview */}
          <motion.div
            {...fadeInUp}
            className="bg-white rounded-lg shadow-lg p-8 mb-8"
          >
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Project Overview
            </h2>
            <p className="text-gray-600 mb-4">
              VisionSleuth AI is a graduate-level forensic science project that performs advanced crime detection 
              using artificial intelligence and computer vision technologies. The system analyzes live camera streams 
              and uploaded video files to detect dangerous objects, suspicious behaviors, and potential security threats 
              in real-time.
            </p>
            <p className="text-gray-600">
              This Master's Thesis project demonstrates the application of state-of-the-art deep learning models, 
              specifically YOLOv8 object detection, combined with forensic analysis methodologies to create a 
              comprehensive crime detection and analysis platform.
            </p>
          </motion.div>

          {/* Key Features */}
          <motion.div
            {...fadeInUp}
            className="bg-white rounded-lg shadow-lg p-8 mb-8"
          >
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Key Features
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="text-lg font-medium text-gray-800 mb-3">Live Camera Analysis</h3>
                <p className="text-gray-600">
                  Real-time crime detection from live camera feeds with frame-by-frame analysis and instant threat assessment.
                </p>
              </div>
              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="text-lg font-medium text-gray-800 mb-3">Video Upload Analysis</h3>
                <p className="text-gray-600">
                  Comprehensive forensic analysis of uploaded video files with detailed detection reports and performance metrics.
                </p>
              </div>
              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="text-lg font-medium text-gray-800 mb-3">Dangerous Object Detection</h3>
                <p className="text-gray-600">
                  Enhanced detection of weapons (knives, handguns) and dangerous objects with high accuracy and low false positive rates.
                </p>
              </div>
              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="text-lg font-medium text-gray-800 mb-3">Professional Forensic Reports</h3>
                <p className="text-gray-600">
                  Advanced forensic-standard English reports with 6 comprehensive sections including executive summary, 
                  behavioral interpretation, and evidential confidence analysis.
                </p>
              </div>
            </div>
          </motion.div>

          {/* Technology Stack */}
          <motion.div
            {...fadeInUp}
            className="bg-white rounded-lg shadow-lg p-8 mb-8"
          >
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Technology Stack
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-gray-800 mb-3">Backend Technologies</h3>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Python & FastAPI
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    YOLOv8 Object Detection
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    OpenCV for Video Processing
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Google Cloud Storage Integration
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-800 mb-3">Frontend Technologies</h3>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Next.js & React
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    TypeScript
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Tailwind CSS
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Real-time WebSocket Communication
                  </li>
                </ul>
              </div>
            </div>
          </motion.div>

          {/* Academic Context */}
          <motion.div
            {...fadeInUp}
            className="bg-white rounded-lg shadow-lg p-8 mb-8"
          >
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Academic Context
            </h2>
            <p className="text-gray-600 mb-4">
              This project is part of a Master's Thesis in Forensic Science, focusing on the application of 
              artificial intelligence and machine learning in forensic video analysis. The system demonstrates 
              how modern deep learning techniques can enhance traditional forensic investigation methods by 
              providing automated, accurate, and comprehensive analysis of video evidence.
            </p>
            <p className="text-gray-600">
              The research addresses critical challenges in forensic science, including real-time threat detection, 
              evidence quality assessment, and the generation of professional forensic reports that meet legal 
              and academic standards.
            </p>
          </motion.div>

          {/* System Capabilities */}
          <motion.div
            {...fadeInUp}
            className="bg-white rounded-lg shadow-lg p-8"
          >
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              System Capabilities
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-4">
                <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-800 mb-2">High Accuracy</h3>
                <p className="text-gray-600">Advanced YOLOv8 models with optimized detection thresholds for reliable results.</p>
              </div>
              <div className="text-center p-4">
                <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-800 mb-2">Real-Time Processing</h3>
                <p className="text-gray-600">Optimized inference pipeline for fast frame-by-frame analysis and instant results.</p>
              </div>
              <div className="text-center p-4">
                <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-800 mb-2">Forensic Reports</h3>
                <p className="text-gray-600">Professional forensic-standard reports with comprehensive analysis and documentation.</p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </main>
      
      <Footer />
    </div>
  );
}

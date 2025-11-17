'use client';

import Header from '@/components/Header';
import Footer from '@/components/Footer';
import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      {/* Video Background */}
      <div className="fixed top-16 left-0 right-0 h-[calc(100vh-4rem)] overflow-hidden">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="absolute w-full h-full object-cover"
          style={{ filter: 'brightness(0.8)' }}
        >
          <source src="/bg-video.mp4" type="video/mp4" />
        </video>
        {/* Overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/30 to-black/20" />
      </div>

      <main className="flex-grow relative">
        <div className="relative z-10 pt-32">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            {/* Hero Section */}
            <div className="text-center mb-16">
              <h1 className="text-5xl font-bold text-white mb-6">
                VisionSleuth AI
              </h1>
              <p className="text-xl text-gray-200 max-w-2xl mx-auto">
                Advanced crime behavior detection through real-time camera analysis and video processing
              </p>
            </div>

            {/* Main Features */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Live Analysis Card */}
              <Link href="/live-analysis">
                <div className="bg-blue-900/40 backdrop-blur-lg rounded-lg shadow-lg overflow-hidden hover:shadow-[0_0_20px_rgba(59,130,246,0.5)] transition-all duration-300 border border-blue-500/30 hover:border-blue-400/50 group">
                  <div className="p-8 relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500/0 to-blue-500/0 group-hover:from-blue-500/10 group-hover:to-blue-500/10 transition-all duration-300" />
                    <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mb-6 relative z-10">
                      <svg
                        className="w-7 h-7 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                        />
                      </svg>
                    </div>
                    <h2 className="text-2xl font-semibold text-white mb-3 relative z-10">
                      Live Camera Analysis
                    </h2>
                    <p className="text-gray-200 relative z-10">
                      Real-time crime behavior detection through live camera feeds
                    </p>
                  </div>
                </div>
              </Link>

              {/* Video Upload Card */}
              <Link href="/video-upload">
                <div className="bg-blue-900/40 backdrop-blur-lg rounded-lg shadow-lg overflow-hidden hover:shadow-[0_0_20px_rgba(59,130,246,0.5)] transition-all duration-300 border border-blue-500/30 hover:border-blue-400/50 group">
                  <div className="p-8 relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500/0 to-blue-500/0 group-hover:from-blue-500/10 group-hover:to-blue-500/10 transition-all duration-300" />
                    <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mb-6 relative z-10">
                      <svg
                        className="w-7 h-7 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        />
                      </svg>
                    </div>
                    <h2 className="text-2xl font-semibold text-white mb-3 relative z-10">
                      Video Upload Analysis
                    </h2>
                    <p className="text-gray-200 relative z-10">
                      Analyze recorded footage for suspicious activities and behaviors
                    </p>
                  </div>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
} 
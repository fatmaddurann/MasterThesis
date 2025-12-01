"use client";
import React from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-16 pt-32">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-800 mb-8">Privacy Policy</h1>
          
          <div className="prose prose-lg max-w-none">
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-700 mb-4">1. Information We Collect</h2>
              <p className="text-gray-600 mb-4">
                VisionSleuth AI collects video data and metadata when you use our video analysis services. 
                We process this information to provide crime detection and analysis features.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-700 mb-4">2. How We Use Your Information</h2>
              <p className="text-gray-600 mb-4">
                We use collected video data solely for the purpose of providing AI-powered crime detection 
                and analysis services. Your data is processed securely and is not shared with third parties 
                without your explicit consent.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-700 mb-4">3. Data Security</h2>
              <p className="text-gray-600 mb-4">
                We implement industry-standard security measures to protect your data. However, no method 
                of transmission over the internet is 100% secure, and we cannot guarantee absolute security.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-700 mb-4">4. Contact Us</h2>
              <p className="text-gray-600 mb-4">
                If you have questions about this Privacy Policy, please contact us through our contact page.
              </p>
            </section>

            <p className="text-sm text-gray-500 mt-8">
              Last updated: {new Date().toLocaleDateString()}
            </p>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
}



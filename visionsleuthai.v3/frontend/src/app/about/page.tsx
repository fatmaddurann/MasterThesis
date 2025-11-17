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
              VisionSleuth AI Hakkında
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Yapay zeka destekli video analiz teknolojimiz ile güvenlik ve analiz çözümleri sunuyoruz.
            </p>
          </div>

          {/* Mission Section */}
          <motion.div
            {...fadeInUp}
            className="bg-white rounded-lg shadow-lg p-8 mb-8"
          >
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Misyonumuz
            </h2>
            <p className="text-gray-600 mb-4">
              VisionSleuth AI olarak, yapay zeka teknolojilerini kullanarak video analiz süreçlerini 
              otomatikleştirmeyi ve güvenlik sistemlerini daha akıllı hale getirmeyi hedefliyoruz. 
              Amacımız, işletmelerin ve kurumların güvenlik ihtiyaçlarını en üst düzeyde karşılamak 
              ve video analiz süreçlerini daha verimli hale getirmektir.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
              <div className="text-center p-4">
                <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-800 mb-2">Güvenlik</h3>
                <p className="text-gray-600">En üst düzey güvenlik standartları ile verilerinizi koruyoruz.</p>
              </div>
              <div className="text-center p-4">
                <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-800 mb-2">Hız</h3>
                <p className="text-gray-600">Yapay zeka destekli hızlı analiz ve işleme süreçleri.</p>
              </div>
              <div className="text-center p-4">
                <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-800 mb-2">İnovasyon</h3>
                <p className="text-gray-600">Sürekli gelişen teknoloji ve yenilikçi çözümler.</p>
              </div>
            </div>
          </motion.div>

          {/* Technology Section */}
          <motion.div
            {...fadeInUp}
            className="bg-white rounded-lg shadow-lg p-8 mb-8"
          >
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Teknolojimiz
            </h2>
            <p className="text-gray-600 mb-6">
              VisionSleuth AI, en son yapay zeka ve makine öğrenimi teknolojilerini kullanarak 
              video analiz süreçlerini otomatikleştiriyor. Sistemimiz, derin öğrenme modelleri 
              ve gelişmiş görüntü işleme algoritmaları ile donatılmıştır.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="text-lg font-medium text-gray-800 mb-3">Yapay Zeka Özellikleri</h3>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Nesne Tespiti ve Takibi
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Hareket Analizi
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Anomali Tespiti
                  </li>
                </ul>
              </div>
              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="text-lg font-medium text-gray-800 mb-3">Teknik Özellikler</h3>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Gerçek Zamanlı İşleme
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Yüksek Doğruluk Oranı
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Ölçeklenebilir Altyapı
                  </li>
                </ul>
              </div>
            </div>
          </motion.div>

          {/* Team Section */}
          <motion.div
            {...fadeInUp}
            className="bg-white rounded-lg shadow-lg p-8"
          >
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Ekibimiz
            </h2>
            <p className="text-gray-600 mb-8">
              VisionSleuth AI, yapay zeka, bilgisayarlı görü ve yazılım geliştirme alanlarında 
              uzmanlaşmış deneyimli bir ekip tarafından yönetilmektedir.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-32 h-32 mx-auto mb-4 rounded-full overflow-hidden bg-gray-200">
                  <img
                    src="/team/ceo.jpg"
                    alt="CEO"
                    className="w-full h-full object-cover"
                  />
                </div>
                <h3 className="text-lg font-medium text-gray-800">Ahmet Yılmaz</h3>
                <p className="text-gray-600">Kurucu & CEO</p>
              </div>
              <div className="text-center">
                <div className="w-32 h-32 mx-auto mb-4 rounded-full overflow-hidden bg-gray-200">
                  <img
                    src="/team/cto.jpg"
                    alt="CTO"
                    className="w-full h-full object-cover"
                  />
                </div>
                <h3 className="text-lg font-medium text-gray-800">Mehmet Demir</h3>
                <p className="text-gray-600">CTO</p>
              </div>
              <div className="text-center">
                <div className="w-32 h-32 mx-auto mb-4 rounded-full overflow-hidden bg-gray-200">
                  <img
                    src="/team/lead.jpg"
                    alt="Lead Developer"
                    className="w-full h-full object-cover"
                  />
                </div>
                <h3 className="text-lg font-medium text-gray-800">Ayşe Kaya</h3>
                <p className="text-gray-600">Lead Developer</p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </main>
      
      <Footer />
    </div>
  );
} 
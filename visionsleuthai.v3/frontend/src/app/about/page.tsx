"use client";
import React, { useState } from "react";
import { motion } from "framer-motion";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { ChevronDownIcon, ChevronUpIcon } from "@heroicons/react/24/outline";

export default function AboutPage() {
  const [expandedSections, setExpandedSections] = useState<{
    supervisor: boolean;
    student: boolean;
  }>({
    supervisor: false,
    student: false,
  });

  const toggleSection = (section: "supervisor" | "student") => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

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
          className="max-w-5xl mx-auto"
        >
          {/* Hero Section */}
          <div className="text-center mb-16">
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              VisionSleuth AI
            </h1>
            <p className="text-2xl text-gray-700 max-w-3xl mx-auto font-light">
              Advanced AI-Powered Forensic Crime Detection System
            </p>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto mt-4">
              Real-Time Video Analysis for Forensic Science Applications
            </p>
          </div>

          {/* Project Overview */}
          <motion.div
            {...fadeInUp}
            className="bg-white rounded-xl shadow-lg p-10 mb-8 border border-gray-100"
          >
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Project Overview</h2>
            <div className="prose prose-lg max-w-none text-gray-700">
              <p className="text-lg leading-relaxed mb-4">
                VisionSleuth AI is a graduate-level forensic science research project that performs advanced 
                crime detection using artificial intelligence and computer vision technologies. The system 
                analyzes live camera streams and uploaded video files to detect dangerous objects, suspicious 
                behaviors, and potential security threats in real-time.
              </p>
              <p className="text-lg leading-relaxed">
                This Master's Thesis project demonstrates the application of state-of-the-art deep learning 
                models, specifically YOLOv8 object detection, combined with forensic analysis methodologies 
                to create a comprehensive crime detection and analysis platform. The research addresses critical 
                challenges in forensic science, including real-time threat detection, evidence quality assessment, 
                and the generation of professional forensic reports that meet legal and academic standards.
              </p>
            </div>
          </motion.div>

          {/* Thesis Credits Section */}
          <motion.div
            {...fadeInUp}
            className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl shadow-lg p-10 mb-8 border border-blue-100"
          >
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Thesis Credits</h2>
            <div className="space-y-6">
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-xl font-semibold text-gray-800 mb-3">Student</h3>
                <p className="text-gray-700 text-lg">
                  <strong>Fatima DURAN</strong><br />
                  MSc Bioinformatics Student<br />
                  Graduate School of Natural Sciences<br />
                  Üsküdar University
                </p>
              </div>
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-xl font-semibold text-gray-800 mb-3">Supervisor</h3>
                <p className="text-gray-700 text-lg">
                  <strong>Prof. Kaan YILANCIOGLU</strong><br />
                  Üsküdar University<br />
                  Institute of Forensic Sciences
                </p>
              </div>
            </div>
          </motion.div>

          {/* Key Features */}
          <motion.div
            {...fadeInUp}
            className="bg-white rounded-xl shadow-lg p-10 mb-8 border border-gray-100"
          >
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Key Features</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
                <h3 className="text-xl font-semibold text-gray-800 mb-3">Live Camera Analysis</h3>
                <p className="text-gray-700">
                  Real-time crime detection from live camera feeds with frame-by-frame analysis and instant threat assessment.
                </p>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
                <h3 className="text-xl font-semibold text-gray-800 mb-3">Video Upload Analysis</h3>
                <p className="text-gray-700">
                  Comprehensive forensic analysis of uploaded video files with detailed detection reports and performance metrics.
                </p>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200">
                <h3 className="text-xl font-semibold text-gray-800 mb-3">Dangerous Object Detection</h3>
                <p className="text-gray-700">
                  Enhanced detection of weapons (knives, handguns) and dangerous objects with high accuracy and low false positive rates.
                </p>
              </div>
              <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-6 border border-orange-200">
                <h3 className="text-xl font-semibold text-gray-800 mb-3">Professional Forensic Reports</h3>
                <p className="text-gray-700">
                  Advanced forensic-standard English reports with 6 comprehensive sections including executive summary, 
                  behavioral interpretation, and evidential confidence analysis.
                </p>
              </div>
            </div>
          </motion.div>

          {/* Technology Stack */}
          <motion.div
            {...fadeInUp}
            className="bg-white rounded-xl shadow-lg p-10 mb-8 border border-gray-100"
          >
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Technology Stack</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold text-gray-800 mb-4">Backend Technologies</h3>
                <ul className="space-y-3 text-gray-700">
                  <li className="flex items-start">
                    <svg className="w-6 h-6 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span><strong>Python & FastAPI</strong> - High-performance backend framework</span>
                  </li>
                  <li className="flex items-start">
                    <svg className="w-6 h-6 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span><strong>YOLOv8</strong> - State-of-the-art object detection model</span>
                  </li>
                  <li className="flex items-start">
                    <svg className="w-6 h-6 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span><strong>OpenCV</strong> - Advanced video processing and computer vision</span>
                  </li>
                  <li className="flex items-start">
                    <svg className="w-6 h-6 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span><strong>Google Cloud Storage</strong> - Scalable data storage and management</span>
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-800 mb-4">Frontend Technologies</h3>
                <ul className="space-y-3 text-gray-700">
                  <li className="flex items-start">
                    <svg className="w-6 h-6 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span><strong>Next.js & React</strong> - Modern web application framework</span>
                  </li>
                  <li className="flex items-start">
                    <svg className="w-6 h-6 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span><strong>TypeScript</strong> - Type-safe development</span>
                  </li>
                  <li className="flex items-start">
                    <svg className="w-6 h-6 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span><strong>Tailwind CSS</strong> - Utility-first styling framework</span>
                  </li>
                  <li className="flex items-start">
                    <svg className="w-6 h-6 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span><strong>WebSocket</strong> - Real-time bidirectional communication</span>
                  </li>
                </ul>
              </div>
            </div>
          </motion.div>

          {/* Ethical Note */}
          <motion.div
            {...fadeInUp}
            className="bg-yellow-50 border-l-4 border-yellow-400 rounded-lg p-6 mb-8"
          >
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Ethical Considerations</h3>
            <p className="text-gray-700 leading-relaxed">
              This research project is conducted with strict adherence to ethical guidelines and privacy protection 
              standards. All video analysis is performed with respect for individual privacy rights, and the system 
              is designed for forensic and security applications in controlled environments. The technology is intended 
              to assist law enforcement and security professionals in evidence analysis, not for unauthorized surveillance.
            </p>
          </motion.div>

          {/* Supervisor CV Section */}
          <motion.div
            {...fadeInUp}
            className="bg-white rounded-xl shadow-lg p-10 mb-8 border border-gray-100"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-3xl font-bold text-gray-900">Supervisor</h2>
              <button
                onClick={() => toggleSection("supervisor")}
                className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium"
              >
                <span>{expandedSections.supervisor ? "Read Less" : "Read More"}</span>
                {expandedSections.supervisor ? (
                  <ChevronUpIcon className="w-5 h-5" />
                ) : (
                  <ChevronDownIcon className="w-5 h-5" />
                )}
              </button>
            </div>
            <div className="mb-4">
              <h3 className="text-2xl font-semibold text-gray-800 mb-2">Prof. Kaan YILANCIOGLU</h3>
              <p className="text-lg text-gray-600 mb-4">
                Associate Professor, Üsküdar University<br />
                Institute of Forensic Sciences
              </p>
            </div>
            {expandedSections.supervisor && (
              <div className="prose prose-lg max-w-none text-gray-700 space-y-4 pt-4 border-t border-gray-200">
                <p className="leading-relaxed">
                  Prof. Kaan YILANCIOGLU was born in Istanbul. He began his higher education at Istanbul University's 
                  Department of Chemical Engineering, and subsequently continued his studies at Istanbul University 
                  Cerrahpaşa Faculty of Medicine, Department of Medical Biological Sciences. During his undergraduate 
                  education, he participated in research at the Academy of Sciences of the Czech Republic, Yeditepe 
                  University, and Çapa Faculty of Medicine.
                </p>
                <p className="leading-relaxed">
                  He was accepted to the International Molecular Medicine master's program at Charité Medical Faculty 
                  in Germany, and began his master's degree with a full scholarship at Sabancı University's Department 
                  of Molecular Biology, Genetics, and Bioengineering. He successfully graduated with a master's thesis 
                  on apoptotic cell signaling pathways induced by original chemotherapeutic molecules in colon cancer cells.
                </p>
                <p className="leading-relaxed">
                  He completed his doctoral education at Sabancı University in the field of biotechnology with a thesis 
                  on the genetic, physiological, and biotechnological evaluation of microorganisms for the production of 
                  renewable, sustainable energy sources. During his doctoral education, he conducted research at the 
                  University of Toronto on drug interactions and multi-drug resistant bacteria. In addition to scientific 
                  articles published in this field, he has published scientific studies in cancer biology, molecular 
                  phylogenetics, and biodiversity.
                </p>
                <p className="leading-relaxed">
                  After his doctorate, he conducted postdoctoral research at Harvard Medical School and Tufts University. 
                  He served as Assistant Director of Üsküdar University's School of Health Services Vocational School and 
                  as Assistant Dean of the Faculty of Engineering and Natural Sciences. Yılancıoğlu, who currently serves 
                  as Assistant Director of the Institute of Addiction and Forensic Sciences and Head of the Department of 
                  Chemical-Biological Engineering, received the title of Associate Professor in 2020.
                </p>
                <div className="mt-6">
                  <h4 className="text-xl font-semibold text-gray-800 mb-3">Research Areas</h4>
                  <ul className="list-disc list-inside space-y-2 text-gray-700">
                    <li>Forensic Sciences</li>
                    <li>Forensic Genetics</li>
                    <li>Molecular Biology</li>
                    <li>Biotechnology</li>
                    <li>Pharmacology (Drug Interactions)</li>
                    <li>Microbiology (Multi-drug Resistant Pathogenic Microorganisms)</li>
                    <li>Molecular Phylogenetics and Biodiversity</li>
                    <li>Cancer Biology</li>
                    <li>Systems Biology</li>
                  </ul>
                </div>
                <p className="leading-relaxed mt-6">
                  In addition to his academic and scientific work, Dr. Yılancıoğlu is one of the founding partners of 
                  SynVera Drug R&D Medical Biotechnology company, established in GOSB TEKNOPARK. Within this company, 
                  he continues patent work on synergistic drug combinations and conducts innovative, technology-based 
                  scientific studies in the medical field. Dr. Yılancıoğlu is fluent in English.
                </p>
              </div>
            )}
          </motion.div>

          {/* Student CV Section */}
          <motion.div
            {...fadeInUp}
            className="bg-white rounded-xl shadow-lg p-10 mb-8 border border-gray-100"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-3xl font-bold text-gray-900">Student</h2>
              <button
                onClick={() => toggleSection("student")}
                className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium"
              >
                <span>{expandedSections.student ? "Read Less" : "Read More"}</span>
                {expandedSections.student ? (
                  <ChevronUpIcon className="w-5 h-5" />
                ) : (
                  <ChevronDownIcon className="w-5 h-5" />
                )}
              </button>
            </div>
            <div className="mb-4">
              <h3 className="text-2xl font-semibold text-gray-800 mb-2">Fatima DURAN</h3>
              <p className="text-lg text-gray-600 mb-4">
                MSc Bioinformatics Student<br />
                Graduate School of Natural Sciences, Üsküdar University
              </p>
            </div>
            {expandedSections.student && (
              <div className="prose prose-lg max-w-none text-gray-700 space-y-4 pt-4 border-t border-gray-200">
                <p className="leading-relaxed">
                  Fatima Duran completed her undergraduate education in Bioengineering at Gaziosmanpaşa University and 
                  is currently pursuing her master's degree in Bioinformatics at Üsküdar University. Within the scope 
                  of her master's thesis, she has developed an artificial intelligence (AI)-based model for crime 
                  analysis from camera feeds, and has also been involved in the design and implementation of various 
                  bioinformatics tools.
                </p>
                <p className="leading-relaxed">
                  She worked as a software developer for three years at LKG Engineering and R&D company, actively 
                  participating in project development, website design, academic reporting, 3D modeling, and software 
                  development processes in wearable technologies, virtual reality (VR), augmented reality (AR), and 
                  AI projects.
                </p>
                <div className="mt-6">
                  <h4 className="text-xl font-semibold text-gray-800 mb-3">Technical Expertise</h4>
                  <ul className="list-disc list-inside space-y-2 text-gray-700">
                    <li><strong>Programming Languages:</strong> Python, R, Node.js, JavaScript</li>
                    <li><strong>Frontend Technologies:</strong> React.js, Next.js, TypeScript</li>
                    <li><strong>AI & Machine Learning:</strong> TensorFlow, Computer Vision, Image Processing</li>
                    <li><strong>Specializations:</strong> AI, Data Analytics, Image Processing, VR/AR, Bioinformatics Applications</li>
                  </ul>
                </div>
                <p className="leading-relaxed mt-6">
                  Her academic and professional work focuses on AI, data analytics, image processing, VR/AR, and 
                  bioinformatics applications. She has developed projects using technologies such as Python, R, Node.js, 
                  React.js, and TensorFlow, gaining experience in both frontend and backend development processes.
                </p>
              </div>
            )}
          </motion.div>
        </motion.div>
      </main>
      
      <Footer />
    </div>
  );
}

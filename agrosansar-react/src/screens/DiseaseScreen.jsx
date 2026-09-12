import React, { useState } from 'react';
import Header from '../components/Header';
import { Camera, Image as ImageIcon, CheckCircle2, AlertTriangle, ShieldCheck, Stethoscope, Sparkles } from 'lucide-react';
import diseaseData from '../data/disease_data.json';

const UI_TEXT = {
  ne: {
    title: 'रोग पहिचान',
    subtitle: 'पातको फोटोबाट रोग पत्ता लगाउनुहोस्',
    cameraScan: 'क्यामेराबाट खिच्नुहोस्',
    uploadGallery: 'ग्यालरीबाट छान्नुहोस्',
    diagnoseBtn: 'रोग पहिचान गर्नुहोस्',
    diagnosing: 'पहिचान गरिँदैछ...',
    resultTitle: 'पहिचान नतिजा',
    symptomsTitle: 'रोगका मुख्य लक्षणहरू',
    treatmentTitle: 'उपचार तथा नियन्त्रण विधि',
    preventionTitle: 'रोकथामका उपायहरू',
    healthyStatus: 'बाली पूर्ण स्वस्थ छ',
    confidence: 'विश्वसनीयता',
    selectPrompt: 'कृपया टमाटरको पातको स्पष्ट फोटो खिच्नुहोस् वा अपलोड गर्नुहोस्।',
  },
  en: {
    title: 'Disease Detection',
    subtitle: 'Identify disease from leaf photo',
    cameraScan: 'Take Photo',
    uploadGallery: 'Upload from Gallery',
    diagnoseBtn: 'Diagnose Disease',
    diagnosing: 'Analyzing Leaf...',
    resultTitle: 'Diagnosis Result',
    symptomsTitle: 'Key Symptoms',
    treatmentTitle: 'Treatment & Control',
    preventionTitle: 'Preventative Measures',
    healthyStatus: 'Plant is Healthy',
    confidence: 'Confidence',
    selectPrompt: 'Please take or upload a clear photo of a tomato leaf.',
  },
};

export default function DiseaseScreen({ language, onToggleLanguage, onBack }) {
  const t = UI_TEXT[language];
  const [selectedImage, setSelectedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [diagnosis, setDiagnosis] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setSelectedImage(event.target.result);
        setDiagnosis(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const runDiagnosis = () => {
    if (!selectedImage) return;
    setIsAnalyzing(true);

    // Simulate smart TFLite inference handoff
    setTimeout(() => {
      // Pick disease class or mock prediction
      const classes = ['Early Blight', 'Late Blight', 'Healthy', 'Leaf Mold'];
      const randomClass = classes[Math.floor(Math.random() * classes.length)];
      const info = diseaseData.info[randomClass]?.[language] || diseaseData.info['Early Blight'][language];
      
      setDiagnosis({
        className: randomClass,
        isHealthy: randomClass === 'Healthy',
        confidence: (88 + Math.random() * 9).toFixed(1),
        info: info,
      });
      setIsAnalyzing(false);
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-[#F6F8F2] flex flex-col max-w-md mx-auto pb-8">
      <Header
        title={t.title}
        subtitle={t.subtitle}
        language={language}
        onToggleLanguage={onToggleLanguage}
        onBack={onBack}
      />

      <div className="px-4 space-y-4 flex-1">
        {/* IMAGE PICKER CARD */}
        <div className="bg-white rounded-[24px] p-5 shadow-sm border border-emerald-950/5 flex flex-col items-center">
          <div className="w-full aspect-[4/3] rounded-2xl bg-[#F6F8F2] border-2 border-dashed border-emerald-900/15 overflow-hidden flex flex-col items-center justify-center relative">
            {selectedImage ? (
              <img src={selectedImage} alt="Selected leaf" className="w-full h-full object-cover" />
            ) : (
              <div className="flex flex-col items-center p-6 text-center">
                <div className="w-14 h-14 rounded-full bg-emerald-100/60 text-[#1D6737] flex items-center justify-center mb-3">
                  <Camera className="w-7 h-7" />
                </div>
                <p className="text-xs text-[#6B736B] max-w-[220px]">
                  {t.selectPrompt}
                </p>
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3 w-full mt-4">
            <label className="flex items-center justify-center space-x-2 py-3 px-4 rounded-xl bg-emerald-50 text-[#1D6737] text-xs font-bold active:scale-95 transition-transform cursor-pointer border border-emerald-900/10">
              <Camera className="w-4 h-4" />
              <span>{t.cameraScan}</span>
              <input type="file" accept="image/*" capture="environment" onChange={handleImageChange} className="hidden" />
            </label>

            <label className="flex items-center justify-center space-x-2 py-3 px-4 rounded-xl bg-gray-50 text-[#3C413C] text-xs font-bold active:scale-95 transition-transform cursor-pointer border border-gray-200">
              <ImageIcon className="w-4 h-4" />
              <span>{t.uploadGallery}</span>
              <input type="file" accept="image/*" onChange={handleImageChange} className="hidden" />
            </label>
          </div>

          {selectedImage && (
            <button
              onClick={runDiagnosis}
              disabled={isAnalyzing}
              className="w-full mt-4 py-3.5 rounded-xl bg-[#1D6737] text-white font-bold text-sm shadow-md flex items-center justify-center space-x-2 active:scale-98 transition-all disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span>{isAnalyzing ? t.diagnosing : t.diagnoseBtn}</span>
            </button>
          )}
        </div>

        {/* DIAGNOSIS RESULTS */}
        {diagnosis && (
          <div className="space-y-4 animate-fadeIn">
            {/* OVERVIEW CARD */}
            <div className="bg-white rounded-[24px] p-5 shadow-sm border border-emerald-950/5">
              <div className="flex items-start justify-between">
                <div>
                  <span className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold mb-2 ${
                    diagnosis.isHealthy ? 'bg-emerald-100 text-[#1D6737]' : 'bg-red-100 text-red-700'
                  }`}>
                    {diagnosis.isHealthy ? (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>{t.healthyStatus}</span>
                      </>
                    ) : (
                      <>
                        <AlertTriangle className="w-3.5 h-3.5" />
                        <span>{diagnosis.className}</span>
                      </>
                    )}
                  </span>

                  <h3 className="text-lg font-extrabold text-[#1D6737]">
                    {diagnosis.info.title}
                  </h3>
                  {diagnosis.info.scientific_name && (
                    <p className="text-xs italic text-gray-500">
                      {diagnosis.info.scientific_name} ({diagnosis.info.pathogen})
                    </p>
                  )}
                </div>

                <div className="text-right">
                  <span className="text-[10px] uppercase font-bold text-gray-400 block">
                    {t.confidence}
                  </span>
                  <span className="text-base font-extrabold text-[#1D6737]">
                    {diagnosis.confidence}%
                  </span>
                </div>
              </div>
            </div>

            {/* SYMPTOMS CARD */}
            {diagnosis.info.symptoms && diagnosis.info.symptoms.length > 0 && (
              <div className="bg-white rounded-[24px] p-5 shadow-sm border border-emerald-950/5 space-y-2.5">
                <h4 className="text-xs font-bold text-[#1D6737] uppercase tracking-wider flex items-center space-x-1.5">
                  <Stethoscope className="w-4 h-4 text-emerald-600" />
                  <span>{t.symptomsTitle}</span>
                </h4>

                <ul className="space-y-2">
                  {diagnosis.info.symptoms.map((sym, idx) => (
                    <li key={idx} className="flex items-start space-x-2 text-xs text-[#3C413C] leading-relaxed">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 mt-1.5 shrink-0" />
                      <span>{sym}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* TREATMENT CARD */}
            {diagnosis.info.treatment && (
              <div className="bg-white rounded-[24px] p-5 shadow-sm border border-emerald-950/5 space-y-2">
                <h4 className="text-xs font-bold text-emerald-800 uppercase tracking-wider flex items-center space-x-1.5">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  <span>{t.treatmentTitle}</span>
                </h4>
                <p className="text-xs text-[#3C413C] leading-relaxed bg-amber-500/5 p-3.5 rounded-xl border border-amber-500/20">
                  {diagnosis.info.treatment}
                </p>
              </div>
            )}

            {/* PREVENTION CARD */}
            {diagnosis.info.prevention && diagnosis.info.prevention.length > 0 && (
              <div className="bg-white rounded-[24px] p-5 shadow-sm border border-emerald-950/5 space-y-2.5">
                <h4 className="text-xs font-bold text-[#1D6737] uppercase tracking-wider flex items-center space-x-1.5">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  <span>{t.preventionTitle}</span>
                </h4>

                <ul className="space-y-2">
                  {diagnosis.info.prevention.map((prev, idx) => (
                    <li key={idx} className="flex items-start space-x-2 text-xs text-[#3C413C] leading-relaxed">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                      <span>{prev}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

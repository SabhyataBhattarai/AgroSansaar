import React from 'react';
import Header from '../components/Header';
import { Sprout, ShieldCheck, Heart, Sparkles, Cpu, Globe2 } from 'lucide-react';

const ABOUT_TEXT = {
  ne: {
    title: 'हाम्रो बारेमा',
    subtitle: 'तपाईंको कृषि सहयोगी',
    appName: 'AgroSansar',
    version: 'संस्करण २.० (React & Capacitor Edition)',
    tagline: 'आधुनिक प्रविधिमार्फत नेपाली कृषिको सशक्तीकरण',
    description:
      'एग्रोसंसार नेपाली कृषकहरूलाई समर्पित एक अत्याधुनिक स्मार्ट कृषि सहायक एप हो। यसले कृत्रिम बौद्धिकता (AI) मार्फत गोलभेँडाको पातको रोग पहिचान, ९० भन्दा बढी कृषि जिज्ञासाको आवाजमा आधारित समाधान, र स्थानीय मौसम पूर्वानुमान प्रदान गर्छ।',
    featuresTitle: 'मुख्य विशेषताहरू',
    features: [
      {
        icon: Sparkles,
        title: 'आवाजमा आधारित कृषि सहायक',
        desc: 'नेपाली र अंग्रेजीमा ९०+ प्रमाणित कृषि प्रश्नहरूको तत्काल उत्तर।',
      },
      {
        icon: Cpu,
        title: 'स्मार्ट रोग पहिचान',
        desc: 'MobileNetV2 आधारित ९३.७५% सही नतिजा दिने रोग पत्ता लगाउने प्रविधि।',
      },
      {
        icon: Globe2,
        title: 'स्थानीय मौसम पूर्वानुमान',
        desc: 'नेपालका प्रमुख शहरहरूको ३ दिने वास्तविक मौसम पूर्वानुमान।',
      },
    ],
    developedWith: 'नेपाली कृषकहरूको समृद्धिका लागि मायापूर्वक निर्मित।',
  },
  en: {
    title: 'About AgroSansar',
    subtitle: 'Your Agriculture Companion',
    appName: 'AgroSansar',
    version: 'Version 2.0 (React & Capacitor Edition)',
    tagline: 'Empowering Nepalese Agriculture with Modern AI',
    description:
      'AgroSansar is an advanced smart agricultural assistant designed for Nepalese farmers. Powered by deep learning, it provides instant tomato leaf disease diagnosis, voice-assisted answers to 90+ agronomic questions, and real-time localized weather forecasts.',
    featuresTitle: 'Key Features',
    features: [
      {
        icon: Sparkles,
        title: 'Voice-Activated Assistant',
        desc: 'Instant spoken and text answers across 90+ verified crop questions.',
      },
      {
        icon: Cpu,
        title: 'AI Disease Diagnosis',
        desc: 'Fine-tuned MobileNetV2 with 93.75% filtered accuracy for leaf health.',
      },
      {
        icon: Globe2,
        title: 'Local Weather Forecast',
        desc: '3-day localized weather data for key agricultural hubs across Nepal.',
      },
    ],
    developedWith: 'Built with care for the empowerment of farming communities.',
  },
};

export default function AboutScreen({ language, onToggleLanguage, onBack }) {
  const t = ABOUT_TEXT[language];

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
        {/* BRAND BANNER */}
        <div className="bg-white rounded-[26px] p-6 shadow-sm border border-emerald-950/5 flex flex-col items-center text-center">
          <div className="w-16 h-16 rounded-2xl bg-[#1D6737] flex items-center justify-center text-white shadow-lg mb-3">
            <Sprout className="w-9 h-9" />
          </div>

          <h2 className="text-2xl font-extrabold text-[#1D6737]">
            {t.appName}
          </h2>
          <span className="text-[11px] font-semibold text-gray-400 mt-0.5">
            {t.version}
          </span>

          <p className="text-xs font-bold text-emerald-800 mt-2 bg-emerald-50 px-3 py-1 rounded-full">
            {t.tagline}
          </p>

          <p className="text-xs text-[#525752] mt-4 leading-relaxed text-justify">
            {t.description}
          </p>
        </div>

        {/* FEATURES LIST */}
        <div className="bg-white rounded-[26px] p-5 shadow-sm border border-emerald-950/5 space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-[#1D6737]">
            {t.featuresTitle}
          </h3>

          <div className="space-y-3">
            {t.features.map((feat, idx) => {
              const Icon = feat.icon;
              return (
                <div key={idx} className="flex items-start space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-emerald-50 text-[#1D6737] flex items-center justify-center shrink-0 mt-0.5">
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-[#2B302B]">
                      {feat.title}
                    </h4>
                    <p className="text-[11px] text-[#6B736B] leading-normal">
                      {feat.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* FOOTER NOTE */}
        <div className="p-4 rounded-2xl bg-white border border-emerald-950/5 text-center flex items-center justify-center space-x-2 text-xs text-[#525752]">
          <Heart className="w-4 h-4 text-red-500 fill-red-500 shrink-0" />
          <span>{t.developedWith}</span>
        </div>
      </div>
    </div>
  );
}

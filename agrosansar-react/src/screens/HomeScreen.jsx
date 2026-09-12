import React, { useMemo } from 'react';
import Header from '../components/Header';
import { Mic, Leaf, CloudSun, Info, ChevronRight, Lightbulb } from 'lucide-react';
import translations from '../data/translations.json';
import dailyTips from '../data/daily_tips.json';

export default function HomeScreen({ language, onToggleLanguage, onNavigate }) {
  const t = translations[language];

  // Daily tip calculated automatically from day of the year (same as Kivy logic)
  const tip = useMemo(() => {
    const tips = dailyTips[language] || [];
    if (tips.length === 0) return '';
    const now = new Date();
    const start = new Date(now.getFullYear(), 0, 0);
    const diff = now - start;
    const oneDay = 1000 * 60 * 60 * 24;
    const dayOfYear = Math.floor(diff / oneDay);
    return tips[dayOfYear % tips.length];
  }, [language]);

  return (
    <div className="min-h-screen bg-[#F6F8F2] flex flex-col pb-6 max-w-md mx-auto">
      {/* 1-TO-1 HEADER */}
      <Header
        title="AgroSansar"
        subtitle={t.tagline}
        language={language}
        onToggleLanguage={onToggleLanguage}
        isHome={true}
      />

      <main className="px-5 pt-1 space-y-4 flex-1">
        {/* PRIMARY FEATURE (Voice Assistant) — HERO CARD (176dp height in Kivy) */}
        <div
          onClick={() => onNavigate('assistant')}
          className="bg-white rounded-[26px] p-5 shadow-sm border border-emerald-950/5 active:scale-[0.98] transition-all cursor-pointer flex items-center space-x-4"
        >
          {/* 72dp green-tinted circular icon card */}
          <div className="w-[72px] h-[72px] rounded-full bg-[#DDEECC] flex items-center justify-center text-[#1D6737] shrink-0 shadow-inner">
            <Mic className="w-9 h-9" />
          </div>

          <div className="flex-1 min-w-0 space-y-1">
            <h2 className="text-[17px] font-bold text-[#1D6737] leading-tight">
              {t.assistant_title}
            </h2>
            <p className="text-[13px] text-[#6B736B] leading-snug">
              {t.assistant_subtitle}
            </p>
            <p className="text-[12px] font-semibold text-[#4A985A] pt-0.5">
              {language === 'ne' ? 'बोल्नुहोस् र उत्तर पाउनुहोस्  ›' : 'Speak to get answers  ›'}
            </p>
          </div>
        </div>

        {/* FEATURE GRID — 2 COLUMNS (1-to-1 with Kivy GridLayout cols: 2) */}
        <div className="grid grid-cols-2 gap-3.5">
          {/* DISEASE DETECTION */}
          <div
            onClick={() => onNavigate('disease')}
            className="bg-white rounded-[22px] p-4 shadow-sm border border-emerald-950/5 active:scale-[0.97] transition-all cursor-pointer flex flex-col justify-between h-[164px]"
          >
            <div className="w-[50px] h-[50px] rounded-[16px] bg-[#DDEECC] flex items-center justify-center text-[#1D6737]">
              <Leaf className="w-7 h-7" />
            </div>

            <div className="mt-2">
              <h3 className="font-bold text-[#252925] text-[15px] leading-snug">
                {t.disease_title}
              </h3>
              <p className="text-[11.5px] text-[#6B736B] leading-tight mt-1 line-clamp-2">
                {t.disease_subtitle.replace('\n', ' ')}
              </p>
            </div>
          </div>

          {/* WEATHER FORECAST */}
          <div
            onClick={() => onNavigate('weather')}
            className="bg-white rounded-[22px] p-4 shadow-sm border border-emerald-950/5 active:scale-[0.97] transition-all cursor-pointer flex flex-col justify-between h-[164px]"
          >
            <div className="w-[50px] h-[50px] rounded-[16px] bg-[#DDEECC] flex items-center justify-center text-[#1D6737]">
              <CloudSun className="w-7 h-7" />
            </div>

            <div className="mt-2">
              <h3 className="font-bold text-[#252925] text-[15px] leading-snug">
                {t.weather_title}
              </h3>
              <p className="text-[11.5px] text-[#6B736B] leading-tight mt-1 line-clamp-2">
                {t.weather_subtitle.replace('\n', ' ')}
              </p>
            </div>
          </div>
        </div>

        {/* ABOUT ROW — (1-to-1 with Kivy 76dp row) */}
        <div
          onClick={() => onNavigate('about')}
          className="bg-white rounded-[20px] p-3.5 shadow-sm border border-emerald-950/5 active:scale-[0.98] transition-all cursor-pointer flex items-center space-x-3.5"
        >
          <div className="w-11 h-11 rounded-[14px] bg-[#F6EFE6] flex items-center justify-center text-[#CD853F] shrink-0">
            <Info className="w-6 h-6" />
          </div>

          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-[#252925] text-[14.5px]">
              {t.about_title}
            </h3>
            <p className="text-[12px] text-[#6B736B] truncate">
              {t.about_subtitle}
            </p>
          </div>

          <div className="text-gray-400">
            <ChevronRight className="w-5 h-5" />
          </div>
        </div>

        {/* TIP OF THE DAY CARD — (1-to-1 with Kivy 118dp card) */}
        <div className="rounded-[20px] p-4 bg-[#F6EFE6] border border-[#ECDCCB] flex items-start space-x-3">
          <div className="w-10 h-10 rounded-[12px] bg-white/70 flex items-center justify-center text-[#CD853F] shrink-0 shadow-xs">
            <Lightbulb className="w-5 h-5" />
          </div>

          <div className="flex-1 min-w-0 space-y-1">
            <h4 className="font-bold text-[13.5px] text-[#996B3D]">
              {language === 'ne' ? 'आजको सुझाव' : 'Tip of the Day'}
            </h4>
            <p className="text-[12px] text-[#665039] leading-relaxed">
              {tip}
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

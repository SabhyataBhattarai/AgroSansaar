import React, { useEffect } from 'react';
import { Sprout } from 'lucide-react';

export default function SplashScreen({ onFinish, language }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onFinish();
    }, 1400);
    return () => clearTimeout(timer);
  }, [onFinish]);

  return (
    <div className="fixed inset-0 bg-[#1D6737] flex flex-col items-center justify-center p-6 text-white select-none z-50 animate-fadeIn">
      <div className="w-24 h-24 rounded-3xl bg-white/10 backdrop-blur-md flex items-center justify-center shadow-2xl mb-6 ring-8 ring-white/5">
        <Sprout className="w-14 h-14 text-white animate-pulse" />
      </div>

      <h1 className="text-3xl font-extrabold tracking-tight mb-2">
        AgroSansar
      </h1>

      <p className="text-sm font-medium text-emerald-100/90 mb-10">
        {language === 'ne' ? 'तपाईंको कृषि सहयोगी' : 'Your Agriculture Companion'}
      </p>

      <div className="w-8 h-8 border-3 border-white/20 border-t-white rounded-full animate-spin" />
    </div>
  );
}

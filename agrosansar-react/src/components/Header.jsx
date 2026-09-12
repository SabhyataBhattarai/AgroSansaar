import React from 'react';
import { ArrowLeft, Sprout } from 'lucide-react';

export default function Header({ 
  title, 
  subtitle, 
  language, 
  onToggleLanguage, 
  onBack, 
  isHome = false 
}) {
  return (
    <header className="flex items-center justify-between px-4 py-3 bg-[#F6F8F2] sticky top-0 z-30">
      <div className="flex items-center space-x-3 flex-1">
        {isHome ? (
          <div className="w-12 h-12 rounded-full shadow-sm flex items-center justify-center overflow-hidden border border-emerald-950/10 bg-white">
            <img 
              src="/icons/icon-192.png" 
              alt="AgroSansar Logo" 
              className="w-full h-full object-cover"
              onError={(e) => {
                e.currentTarget.style.display = 'none';
              }}
            />
          </div>
        ) : (
          <button
            onClick={onBack}
            className="p-2 -ml-2 rounded-full text-[#1D6737] hover:bg-emerald-50 active:scale-95 transition-all"
            aria-label="Back"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
        )}

        <div className="flex flex-col">
          <h1 className="text-xl font-bold text-[#1D6737] leading-tight">
            {title}
          </h1>
          {subtitle && (
            <p className="text-xs text-[#6B736B] font-medium leading-tight">
              {subtitle}
            </p>
          )}
        </div>
      </div>

      <button
        onClick={onToggleLanguage}
        className="px-3.5 py-1.5 rounded-full bg-[#DDEED8] text-[#1D6737] font-bold text-sm shadow-xs active:scale-95 transition-transform"
      >
        {language === 'ne' ? 'EN' : 'ने'}
      </button>
    </header>
  );
}

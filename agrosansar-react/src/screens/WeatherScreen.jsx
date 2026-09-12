import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { CloudSun, Droplets, Wind, MapPin, ChevronDown, RefreshCw, AlertCircle } from 'lucide-react';

const API_KEY = '8ccd400ba27344f9b30191926260907';

const CITIES = [
  { en: 'Kathmandu', ne: 'काठमाडौं' },
  { en: 'Biratnagar', ne: 'विराटनगर' },
  { en: 'Hetauda', ne: 'हेटौंडा' },
  { en: 'Jhapa', ne: 'झापा' },
  { en: 'Chitwan', ne: 'चितवन' },
  { en: 'Nepalgunj', ne: 'नेपालगञ्ज' },
  { en: 'Taplejung', ne: 'ताप्लेजुङ' },
  { en: 'Solukhumbu', ne: 'सोलुखुम्बु' },
];

const WEATHER_TRANSLATIONS = {
  'Sunny': 'घाम लागेको',
  'Clear': 'सफा मौसम',
  'Partly cloudy': 'आंशिक बदली',
  'Cloudy': 'बादल लागेको',
  'Overcast': 'घना बदली',
  'Mist': 'कुहिरो',
  'Fog': 'हुस्सु',
  'Patchy rain nearby': 'छिटपुट वर्षा',
  'Patchy light rain': 'हल्का वर्षा',
  'Light rain': 'हल्का वर्षा',
  'Moderate rain': 'मध्यम वर्षा',
  'Heavy rain': 'भारी वर्षा',
  'Thunderstorm': 'चट्याङसहित वर्षा',
};

const UI_TEXT = {
  ne: {
    title: 'मौसम जानकारी',
    subtitle: 'तपाईंको कृषि सहयोगी',
    humidity: 'आर्द्रता',
    wind: 'हावा',
    loading: 'मौसम लोड हुँदैछ...',
    error: 'मौसम डेटा लोड गर्न सकिएन।',
    days: ['आज', 'भोलि', 'पर्सि'],
  },
  en: {
    title: 'Weather Information',
    subtitle: 'Your Agriculture Companion',
    humidity: 'Humidity',
    wind: 'Wind',
    loading: 'Loading Weather...',
    error: 'Failed to load weather data.',
    days: ['Today', 'Tomorrow', 'Day After'],
  },
};

export default function WeatherScreen({ language, onToggleLanguage, onBack }) {
  const t = UI_TEXT[language];
  const [selectedCity, setSelectedCity] = useState(CITIES[0]);
  const [weatherData, setWeatherData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  const fetchWeather = async (cityObj) => {
    setIsLoading(true);
    setHasError(false);
    try {
      const res = await fetch(
        `https://api.weatherapi.com/v1/forecast.json?key=${API_KEY}&q=${cityObj.en}&days=3`
      );
      if (!res.ok) throw new Error('API Error');
      const data = await res.json();
      setWeatherData(data);
    } catch (err) {
      console.warn('Weather fetch error:', err);
      setHasError(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchWeather(selectedCity);
  }, [selectedCity]);

  const translateCondition = (cond) => {
    if (language === 'en') return cond;
    return WEATHER_TRANSLATIONS[cond] || cond;
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
        {/* CITY SELECTOR */}
        <div className="flex items-center justify-between bg-white rounded-2xl p-3 shadow-xs border border-emerald-950/5">
          <div className="flex items-center space-x-2 text-[#1D6737]">
            <MapPin className="w-5 h-5" />
            <span className="text-xs font-bold uppercase tracking-wider text-gray-400">
              {language === 'ne' ? 'स्थान:' : 'Location:'}
            </span>
          </div>

          <div className="relative">
            <select
              value={selectedCity.en}
              onChange={(e) => {
                const found = CITIES.find((c) => c.en === e.target.value);
                if (found) setSelectedCity(found);
              }}
              className="appearance-none bg-[#F6F8F2] text-[#1D6737] font-bold text-sm py-1.5 pl-3 pr-8 rounded-xl focus:outline-none cursor-pointer"
            >
              {CITIES.map((c) => (
                <option key={c.en} value={c.en}>
                  {language === 'ne' ? c.ne : c.en}
                </option>
              ))}
            </select>
            <ChevronDown className="w-4 h-4 text-[#1D6737] absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>
        </div>

        {/* LOADING & ERROR STATES */}
        {isLoading && (
          <div className="bg-white rounded-[24px] p-8 flex flex-col items-center justify-center space-y-3 shadow-sm">
            <RefreshCw className="w-8 h-8 text-[#1D6737] animate-spin" />
            <p className="text-xs text-[#6B736B] font-medium">{t.loading}</p>
          </div>
        )}

        {hasError && !isLoading && (
          <div className="bg-white rounded-[24px] p-6 text-center space-y-3 shadow-sm border border-red-100">
            <AlertCircle className="w-8 h-8 text-red-500 mx-auto" />
            <p className="text-xs text-red-700 font-medium">{t.error}</p>
            <button
              onClick={() => fetchWeather(selectedCity)}
              className="px-4 py-2 rounded-xl bg-emerald-50 text-[#1D6737] text-xs font-bold"
            >
              Retry
            </button>
          </div>
        )}

        {/* CURRENT WEATHER HERO */}
        {!isLoading && weatherData && (
          <>
            <div className="bg-gradient-to-br from-[#1D6737] to-[#124423] rounded-[26px] p-6 text-white shadow-lg relative overflow-hidden">
              <div className="flex items-start justify-between relative z-10">
                <div>
                  <h2 className="text-xl font-extrabold tracking-tight">
                    {language === 'ne' ? selectedCity.ne : selectedCity.en}
                  </h2>
                  <p className="text-xs text-emerald-100/90 font-medium mt-0.5">
                    {translateCondition(weatherData.current.condition.text)}
                  </p>
                </div>

                <img
                  src={`https:${weatherData.current.condition.icon}`}
                  alt="weather"
                  className="w-14 h-14 object-contain"
                />
              </div>

              <div className="mt-4 flex items-baseline relative z-10">
                <span className="text-5xl font-extrabold tracking-tighter">
                  {Math.round(weatherData.current.temp_c)}
                </span>
                <span className="text-2xl font-bold ml-1">°C</span>
              </div>

              {/* STATS BAR */}
              <div className="grid grid-cols-2 gap-3 mt-6 pt-4 border-t border-white/10 relative z-10">
                <div className="flex items-center space-x-2.5">
                  <Droplets className="w-4 h-4 text-sky-300" />
                  <div>
                    <span className="text-[10px] text-emerald-100/70 block uppercase font-bold">
                      {t.humidity}
                    </span>
                    <span className="text-xs font-bold">
                      {weatherData.current.humidity}%
                    </span>
                  </div>
                </div>

                <div className="flex items-center space-x-2.5">
                  <Wind className="w-4 h-4 text-emerald-200" />
                  <div>
                    <span className="text-[10px] text-emerald-100/70 block uppercase font-bold">
                      {t.wind}
                    </span>
                    <span className="text-xs font-bold">
                      {weatherData.current.wind_kph} km/h
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* 3-DAY FORECAST */}
            <div className="space-y-2">
              <h3 className="text-xs font-bold text-[#6B736B] uppercase tracking-wider px-1">
                {language === 'ne' ? '३ दिने मौसम पूर्वानुमान' : '3-Day Forecast'}
              </h3>

              <div className="space-y-2">
                {weatherData.forecast.forecastday.map((day, idx) => (
                  <div
                    key={idx}
                    className="bg-white rounded-2xl p-3.5 shadow-xs border border-emerald-950/5 flex items-center justify-between"
                  >
                    <div className="flex items-center space-x-3">
                      <img
                        src={`https:${day.day.condition.icon}`}
                        alt="icon"
                        className="w-9 h-9 object-contain"
                      />
                      <div>
                        <h4 className="text-xs font-bold text-[#1D6737]">
                          {t.days[idx] || day.date}
                        </h4>
                        <p className="text-[11px] text-gray-500">
                          {translateCondition(day.day.condition.text)}
                        </p>
                      </div>
                    </div>

                    <div className="text-right">
                      <span className="text-xs font-extrabold text-[#1D6737]">
                        {Math.round(day.day.maxtemp_c)}° /{' '}
                        <span className="text-gray-400 font-medium">
                          {Math.round(day.day.mintemp_c)}°
                        </span>
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

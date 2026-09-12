import React, { useState } from 'react';
import SplashScreen from './screens/SplashScreen';
import HomeScreen from './screens/HomeScreen';
import AssistantScreen from './screens/AssistantScreen';
import DiseaseScreen from './screens/DiseaseScreen';
import WeatherScreen from './screens/WeatherScreen';
import AboutScreen from './screens/AboutScreen';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('splash');
  const [language, setLanguage] = useState('ne');

  const toggleLanguage = () => {
    setLanguage((prev) => (prev === 'ne' ? 'en' : 'ne'));
  };

  return (
    <div className="w-full min-h-screen bg-[#F6F8F2] font-sans antialiased text-gray-900 selection:bg-emerald-200">
      {currentScreen === 'splash' && (
        <SplashScreen
          language={language}
          onFinish={() => setCurrentScreen('home')}
        />
      )}

      {currentScreen === 'home' && (
        <HomeScreen
          language={language}
          onToggleLanguage={toggleLanguage}
          onNavigate={(screen) => setCurrentScreen(screen)}
        />
      )}

      {currentScreen === 'assistant' && (
        <AssistantScreen
          language={language}
          onToggleLanguage={toggleLanguage}
          onBack={() => setCurrentScreen('home')}
        />
      )}

      {currentScreen === 'disease' && (
        <DiseaseScreen
          language={language}
          onToggleLanguage={toggleLanguage}
          onBack={() => setCurrentScreen('home')}
        />
      )}

      {currentScreen === 'weather' && (
        <WeatherScreen
          language={language}
          onToggleLanguage={toggleLanguage}
          onBack={() => setCurrentScreen('home')}
        />
      )}

      {currentScreen === 'about' && (
        <AboutScreen
          language={language}
          onToggleLanguage={toggleLanguage}
          onBack={() => setCurrentScreen('home')}
        />
      )}
    </div>
  );
}

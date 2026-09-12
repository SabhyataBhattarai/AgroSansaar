import React, { useState, useEffect, useRef } from 'react';
import Header from '../components/Header';
import { HelpCircle, Volume2, VolumeX, Mic, MicOff, Send, Sparkles, AlertCircle, RefreshCw } from 'lucide-react';
import Fuse from 'fuse.js';
import qaData from '../data/qa_data.json';
import { speechService, ttsService } from '../services/speechService';

const UI_TEXT = {
  ne: {
    title: 'कृषि सहायक',
    subtitle: 'तपाईंको कृषि सहयोगी',
    questionPlaceholder: 'तपाईंले सोध्नुभएको प्रश्न यहाँ देखिनेछ।',
    answerPlaceholder: 'तपाईंको उत्तर यहाँ देखिनेछ।',
    answerTitle: 'उत्तर',
    suggestionsTitle: 'उदाहरण प्रश्नहरू',
    micInstruction: 'प्रश्न सोध्न माइक्रोफोन थिच्नुहोस्',
    listening: 'सुन्दैछ... कृपया बोल्नुहोस्',
    fallback: 'माफ गर्नुहोस्, मैले तपाईंको प्रश्न बुझिनँ।',
    examples: [
      '•  मल भनेको के हो?',
      '•  गोलभेँडामा कुन मल हाल्ने?',
      '•  गोलभेँडा कुन मौसममा लगाइन्छ?',
      '•  गोलभेँडाको पात किन पहेंलो हुन्छ?',
      '•  गोलभेँडामा रोग लागेको कसरी थाहा पाउने?',
    ],
  },
  en: {
    title: 'Agriculture Assistant',
    subtitle: 'Your Agriculture Companion',
    questionPlaceholder: 'Your question will appear here.',
    answerPlaceholder: 'Your answer will appear here.',
    answerTitle: 'Answer',
    suggestionsTitle: 'Example Questions',
    micInstruction: 'Tap microphone to ask a question',
    listening: 'Listening... please speak',
    fallback: "Sorry, I couldn't understand your question.",
    examples: [
      '•  What is fertilizer?',
      '•  How do I know if my tomato plant has a disease?',
      '•  When is the best time to grow tomatoes?',
      '•  Why are my tomato leaves turning yellow?',
      '•  How much water do tomatoes need?',
    ],
  },
};

export default function AssistantScreen({ language, onToggleLanguage, onBack }) {
  const t = UI_TEXT[language];
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [textInput, setTextInput] = useState('');
  
  const audioRef = useRef(null);
  const recognitionRef = useRef(null);

  // Initialize Fuzzy Search Index with Fuse.js
  const fuseRef = useRef(null);
  useEffect(() => {
    const list = qaData[language] || [];
    fuseRef.current = new Fuse(list, {
      keys: ['question'],
      includeScore: true,
      threshold: 0.45,
      ignoreLocation: true,
    });
  }, [language]);

  // Answer matching query
  const findAnswer = (query) => {
    if (!query || !fuseRef.current) return;
    const clean = query.replace('•', '').trim();
    setQuestion(clean);

    const results = fuseRef.current.search(clean);
    let matchedAnswer = t.fallback;
    if (results && results.length > 0 && results[0].score <= 0.45) {
      matchedAnswer = results[0].item.answer;
    }
    setAnswer(matchedAnswer);
    speakText(matchedAnswer);
  };

  // Text-To-Speech (Native Android TTS + Browser Web Speech + Audio stream fallback)
  const speakText = async (text) => {
    if (!text || text === t.fallback) return;
    try {
      await ttsService.speak(
        text,
        language,
        () => setIsSpeaking(true),
        () => setIsSpeaking(false)
      );
    } catch (e) {
      console.warn('speakText error:', e);
      setIsSpeaking(false);
    }
  };

  const stopSpeaking = async () => {
    try {
      await ttsService.stop();
    } catch (e) {}
    setIsSpeaking(false);
  };

  const [permissionError, setPermissionError] = useState(null);
  const [isRequestingPermission, setIsRequestingPermission] = useState(false);

  // Speech-To-Text (Microphone) with cross-platform permission handling
  const toggleListening = async () => {
    if (isListening) {
      await stopListening();
      return;
    }

    setPermissionError(null);
    setIsRequestingPermission(true);
    stopSpeaking();

    try {
      const recognitionInstance = await speechService.startListening({
        language,
        onStart: () => {
          setIsRequestingPermission(false);
          setIsListening(true);
        },
        onResult: (transcript) => {
          findAnswer(transcript);
        },
        onError: (errCode) => {
          setIsListening(false);
          setIsRequestingPermission(false);
          if (errCode === 'PERMISSION_DENIED') {
            setPermissionError(
              language === 'ne'
                ? 'माइक्रोफोन अनुमति अस्वीकार गरियो। कृपया ब्राउजरको URL पट्टीमा भएको लक/माइक आइकनमा क्लिक गरी अनुमति दिनुहोस्।'
                : 'Microphone permission was denied. Please click the mic/lock icon in your browser URL bar to allow access.'
            );
          } else if (errCode === 'SECURE_ORIGIN_REQUIRED') {
            setPermissionError(
              language === 'ne'
                ? 'ब्राउजर सुरक्षाका कारण मोबाइल ब्राउजरमा माइक चलाउन HTTPS वा localhost आवश्यक पर्दछ। तल टाइप गरी सोध्न सक्नुहुन्छ वा Native APK प्रयोग गर्न सक्नुहुन्छ।'
                : 'Microphone requires HTTPS or localhost when accessed on mobile browsers. Please type your question below or use the APK.'
            );
          } else if (errCode === 'NOT_SUPPORTED' || errCode === 'NOT_AVAILABLE') {
            setPermissionError(
              language === 'ne'
                ? 'यस उपकरणमा स्वचालित आवाज पहिचान उपलब्ध छैन। कृपया तल टाइप गर्नुहोस्।'
                : 'Speech recognition is not supported on this browser/device. Please type below.'
            );
          } else if (errCode !== 'NO_SPEECH') {
            setPermissionError(
              language === 'ne'
                ? `माइक समस्या: ${errCode}। कृपया तल टाइप गर्नुहोस्।`
                : `Microphone issue: ${errCode}. Please type below.`
            );
          }
        },
        onEnd: () => {
          setIsListening(false);
          setIsRequestingPermission(false);
        },
      });

      recognitionRef.current = recognitionInstance;
    } catch (err) {
      console.error('Error starting listening:', err);
      setIsListening(false);
      setIsRequestingPermission(false);
    }
  };

  const stopListening = async () => {
    await speechService.stopListening(recognitionRef.current);
    setIsListening(false);
    setIsRequestingPermission(false);
  };

  const handleManualSubmit = (e) => {
    e.preventDefault();
    if (textInput.trim()) {
      findAnswer(textInput);
      setTextInput('');
    }
  };

  return (
    <div className="min-h-screen bg-[#F6F8F2] flex flex-col max-w-md mx-auto pb-6">
      <Header
        title={t.title}
        subtitle={t.subtitle}
        language={language}
        onToggleLanguage={onToggleLanguage}
        onBack={onBack}
      />

      <div className="px-4 space-y-4 flex-1 flex flex-col pt-1">
        {/* RECOGNIZED QUESTION CARD */}
        <div className="bg-white rounded-2xl p-3.5 shadow-xs border border-emerald-950/5 flex items-center space-x-3">
          <HelpCircle className="w-5 h-5 text-[#1D6737] shrink-0" />
          <p className="text-xs font-medium text-[#4A504A] truncate">
            {question || t.questionPlaceholder}
          </p>
        </div>

        {/* ANSWER CARD */}
        <div className="bg-white rounded-[24px] p-5 shadow-sm border border-emerald-950/5 flex-1 flex flex-col min-h-[160px] relative">
          <div className="flex items-center justify-between border-b border-gray-100 pb-3 mb-3">
            <span className="text-sm font-bold text-[#1D6737] flex items-center space-x-1.5">
              <Sparkles className="w-4 h-4 text-emerald-600" />
              <span>{t.answerTitle}</span>
            </span>

            {answer && (
              <button
                onClick={() => (isSpeaking ? stopSpeaking() : speakText(answer))}
                className="p-1.5 rounded-full text-[#1D6737] hover:bg-emerald-50 active:scale-95 transition-all"
                aria-label="Play or stop voice"
              >
                {isSpeaking ? (
                  <VolumeX className="w-5 h-5 text-amber-600 animate-pulse" />
                ) : (
                  <Volume2 className="w-5 h-5" />
                )}
              </button>
            )}
          </div>

          <div className="flex-1 overflow-y-auto pr-1">
            <p className="text-xs sm:text-sm text-[#2B302B] leading-relaxed">
              {answer || t.answerPlaceholder}
            </p>
          </div>
        </div>

        {/* SUGGESTIONS PILLS */}
        <div className="space-y-2">
          <h3 className="text-xs font-bold text-[#6B736B] uppercase tracking-wider px-1">
            {t.suggestionsTitle}
          </h3>

          <div className="space-y-1.5 max-h-[160px] overflow-y-auto pr-1">
            {t.examples.map((item, index) => (
              <button
                key={index}
                onClick={() => findAnswer(item)}
                className="w-full text-left p-2.5 rounded-xl bg-white border border-emerald-900/5 hover:border-emerald-500/30 text-xs font-medium text-[#1D6737] active:scale-[0.99] transition-all shadow-xs flex items-center justify-between"
              >
                <span className="truncate">{item}</span>
              </button>
            ))}
          </div>
        </div>

        {/* MANUAL TEXT INPUT (Optional helper) */}
        <form onSubmit={handleManualSubmit} className="flex items-center space-x-2 pt-1">
          <input
            type="text"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder={language === 'ne' ? 'यहाँ प्रश्न टाइप गर्नुहोस्...' : 'Type question here...'}
            className="flex-1 bg-white border border-emerald-900/10 rounded-full px-4 py-2.5 text-xs text-[#2B302B] focus:outline-none focus:ring-2 focus:ring-[#1D6737]/30 shadow-xs"
          />
          <button
            type="submit"
            disabled={!textInput.trim()}
            className="w-10 h-10 rounded-full bg-[#1D6737] text-white flex items-center justify-center disabled:opacity-40 active:scale-95 transition-all shadow-xs shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>

        {/* PERMISSION ERROR BANNER */}
        {permissionError && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-3 flex items-start space-x-2.5 animate-fadeIn">
            <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div className="flex-1 text-xs text-amber-900 leading-relaxed">
              <p>{permissionError}</p>
            </div>
            <button
              onClick={() => setPermissionError(null)}
              className="text-amber-500 hover:text-amber-800 text-xs font-bold px-1"
            >
              ✕
            </button>
          </div>
        )}

        {/* FLOATING MICROPHONE BUTTON */}
        <div className="flex flex-col items-center justify-center pt-1 pb-1">
          <button
            onClick={toggleListening}
            disabled={isRequestingPermission}
            className={`w-16 h-16 rounded-full flex items-center justify-center text-white shadow-lg active:scale-95 transition-all relative ${
              isListening
                ? 'bg-red-500 ring-8 ring-red-400/30 animate-pulse'
                : isRequestingPermission
                ? 'bg-amber-600 animate-pulse'
                : 'bg-[#1D6737] hover:bg-emerald-800'
            }`}
          >
            {isRequestingPermission ? (
              <RefreshCw className="w-7 h-7 animate-spin" />
            ) : isListening ? (
              <MicOff className="w-8 h-8" />
            ) : (
              <Mic className="w-8 h-8" />
            )}
          </button>

          <p className="text-[11.5px] font-medium text-[#6B736B] mt-2">
            {isRequestingPermission
              ? (language === 'ne' ? 'अनुमति माग्दैछ... कृपया Allow गर्नुहोस्' : 'Requesting mic permission... please click Allow')
              : isListening
              ? t.listening
              : t.micInstruction}
          </p>
        </div>
      </div>
    </div>
  );
}

import { Capacitor } from '@capacitor/core';
import { SpeechRecognition as CapSpeechRecognition } from '@capacitor-community/speech-recognition';
import { TextToSpeech } from '@capacitor-community/text-to-speech';

/**
 * Cross-platform Speech Recognition & Microphone Permission Service
 * Supports:
 * 1. Native Android / iOS via @capacitor-community/speech-recognition
 * 2. Modern Web Browsers via Web Speech API + getUserMedia permission prompt
 */
export const speechService = {
  isNative: Capacitor.isNativePlatform(),

  /**
   * Request microphone permissions explicitly
   */
  async requestPermission() {
    if (this.isNative) {
      try {
        const check = await CapSpeechRecognition.checkPermissions();
        if (check && check.speechRecognition !== 'granted') {
          const req = await CapSpeechRecognition.requestPermissions();
          return req && req.speechRecognition === 'granted';
        }
        return true;
      } catch (e) {
        console.warn('Native permission check failed:', e);
        // Try requesting directly if check fails
        try {
          const req = await CapSpeechRecognition.requestPermissions();
          return req && req.speechRecognition === 'granted';
        } catch (err) {
          console.error('Direct requestPermissions failed:', err);
          return false;
        }
      }
    } else {
      // Browser environment
      if (!window.isSecureContext && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        throw new Error('SECURE_ORIGIN_REQUIRED');
      }

      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          stream.getTracks().forEach((track) => track.stop());
          return true;
        } catch (err) {
          if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
            throw new Error('PERMISSION_DENIED');
          }
          throw err;
        }
      }
      return true;
    }
  },

  /**
   * Start listening for voice input
   */
  async startListening({ language, onResult, onError, onStart, onEnd }) {
    const langCode = language === 'ne' ? 'ne-NP' : 'en-US';

    if (this.isNative) {
      try {
        const permGranted = await this.requestPermission();
        if (!permGranted) {
          onError && onError('PERMISSION_DENIED');
          return;
        }

        try {
          const available = await CapSpeechRecognition.available();
          if (!available.available) {
            console.warn('Recognition not marked available, attempting start anyway...');
          }
        } catch (e) {
          console.warn('Available check error:', e);
        }

        onStart && onStart();

        // Native Android speech recognition with native popup
        const result = await CapSpeechRecognition.start({
          language: langCode,
          maxResults: 3,
          prompt: language === 'ne' ? 'तपाईंको कृषि प्रश्न सोध्नुहोस्...' : 'Ask your farming question...',
          partialResults: false,
          popup: true,
        });

        if (result && result.matches && result.matches.length > 0) {
          onResult && onResult(result.matches[0]);
        }
        onEnd && onEnd();
      } catch (err) {
        console.error('Native speech error:', err);
        const msg = String(err && err.message ? err.message : err);
        if (msg.toLowerCase().includes('permission') || msg.toLowerCase().includes('denied')) {
          onError && onError('PERMISSION_DENIED');
        } else {
          onError && onError(msg || 'NATIVE_ERROR');
        }
        onEnd && onEnd();
      }
    } else {
      // Web / Browser Speech Recognition
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

      if (!SpeechRecognition) {
        onError && onError('NOT_SUPPORTED');
        return;
      }

      try {
        await this.requestPermission();
      } catch (permErr) {
        if (permErr.message === 'SECURE_ORIGIN_REQUIRED') {
          onError && onError('SECURE_ORIGIN_REQUIRED');
          return;
        }
        onError && onError('PERMISSION_DENIED');
        return;
      }

      try {
        const recognition = new SpeechRecognition();
        recognition.lang = langCode;
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
          onStart && onStart();
        };

        recognition.onresult = (event) => {
          if (event.results && event.results[0] && event.results[0][0]) {
            const transcript = event.results[0][0].transcript;
            onResult && onResult(transcript);
          }
        };

        recognition.onerror = (event) => {
          console.warn('Web speech error:', event.error);
          if (event.error === 'not-allowed') {
            onError && onError('PERMISSION_DENIED');
          } else if (event.error === 'no-speech') {
            onError && onError('NO_SPEECH');
          } else {
            onError && onError(event.error);
          }
        };

        recognition.onend = () => {
          onEnd && onEnd();
        };

        recognition.start();
        return recognition;
      } catch (err) {
        console.error('Speech recognition start failed:', err);
        onError && onError(err.message || 'START_FAILED');
        onEnd && onEnd();
      }
    }
  },

  /**
   * Stop listening
   */
  async stopListening(recognitionInstance) {
    if (this.isNative) {
      try {
        await CapSpeechRecognition.stop();
        await CapSpeechRecognition.removeAllListeners();
      } catch (e) {
        console.warn('Native speech stop error:', e);
      }
    } else if (recognitionInstance) {
      try {
        recognitionInstance.stop();
      } catch (e) {
        console.warn('Web speech stop error:', e);
      }
    }
  }
};

/**
 * Cross-platform Text-To-Speech (Native Android TextToSpeech + Browser Web Speech + Google TTS Stream fallback)
 */
export const ttsService = {
  isNative: Capacitor.isNativePlatform(),
  currentAudio: null,

  async speak(text, language = 'ne', onStart, onEnd) {
    await this.stop();
    if (!text) return;

    const langCode = language === 'ne' ? 'ne-NP' : 'en-US';

    // 1. Native Capacitor TTS (Uses Android's native TextToSpeech engine)
    if (this.isNative) {
      try {
        onStart && onStart();
        await TextToSpeech.speak({
          text,
          lang: langCode,
          rate: 0.95,
          pitch: 1.0,
          volume: 1.0,
          category: 'playback',
        });
        onEnd && onEnd();
        return;
      } catch (err) {
        console.warn('Native TextToSpeech failed, falling back to audio stream:', err);
      }
    }

    // 2. Web Speech Synthesis (Browser)
    if ('speechSynthesis' in window && !this.isNative) {
      try {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = langCode;
        utterance.rate = 0.95;
        utterance.onstart = () => onStart && onStart();
        utterance.onend = () => onEnd && onEnd();
        utterance.onerror = () => {
          this.fallbackAudioStream(text, language, onStart, onEnd);
        };
        window.speechSynthesis.speak(utterance);
        return;
      } catch (e) {
        console.warn('speechSynthesis failed, falling back to stream:', e);
      }
    }

    // 3. Audio Stream Fallback (Works everywhere with internet access)
    this.fallbackAudioStream(text, language, onStart, onEnd);
  },

  fallbackAudioStream(text, language, onStart, onEnd) {
    try {
      const tl = language === 'ne' ? 'ne' : 'en';
      const cleanText = text.replace(/[•\n]/g, ' ').slice(0, 150);
      const url = `https://translate.google.com/translate_tts?ie=UTF-8&q=${encodeURIComponent(cleanText)}&tl=${tl}&client=tw-ob`;
      
      const audio = new Audio(url);
      this.currentAudio = audio;
      audio.onplay = () => onStart && onStart();
      audio.onended = () => {
        this.currentAudio = null;
        onEnd && onEnd();
      };
      audio.onerror = (e) => {
        console.warn('Audio stream playback failed:', e);
        this.currentAudio = null;
        onEnd && onEnd();
      };
      audio.play().catch((err) => {
        console.warn('audio.play() error:', err);
        onEnd && onEnd();
      });
    } catch (err) {
      console.warn('Audio stream error:', err);
      onEnd && onEnd();
    }
  },

  async stop() {
    if (this.isNative) {
      try {
        await TextToSpeech.stop();
      } catch (e) {}
    }
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio = null;
    }
  }
};

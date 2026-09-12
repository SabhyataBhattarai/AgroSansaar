import { Capacitor } from '@capacitor/core';
import { SpeechRecognition as CapSpeechRecognition } from '@capacitor-community/speech-recognition';

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
        const has = await CapSpeechRecognition.hasPermissions();
        if (!has.permission) {
          const res = await CapSpeechRecognition.requestPermissions();
          return !!res.permission;
        }
        return true;
      } catch (e) {
        console.warn('Native permission check failed:', e);
        return false;
      }
    } else {
      // Browser environment
      if (!window.isSecureContext && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        throw new Error('SECURE_ORIGIN_REQUIRED');
      }

      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          // Stop stream tracks immediately once permission is verified
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
        const perm = await this.requestPermission();
        if (!perm) {
          onError && onError('PERMISSION_DENIED');
          return;
        }

        const available = await CapSpeechRecognition.available();
        if (!available.available) {
          onError && onError('NOT_AVAILABLE');
          return;
        }

        onStart && onStart();

        CapSpeechRecognition.addListener('partialResults', (data) => {
          if (data && data.matches && data.matches.length > 0) {
            onResult && onResult(data.matches[0]);
          }
        });

        const result = await CapSpeechRecognition.start({
          language: langCode,
          maxResults: 2,
          prompt: language === 'ne' ? 'बोल्नुहोस्...' : 'Speak now...',
          partialResults: false,
          popup: false,
        });

        if (result && result.matches && result.matches.length > 0) {
          onResult && onResult(result.matches[0]);
        }
        onEnd && onEnd();
      } catch (err) {
        console.error('Native speech error:', err);
        onError && onError(err.message || 'NATIVE_ERROR');
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
        // Explicitly trigger browser permission prompt if needed
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

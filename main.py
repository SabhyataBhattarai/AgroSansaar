import os
gtk_bin = r"C:\Program Files\GTK3-Runtime Win64\bin"
if os.path.exists(gtk_bin):
    os.add_dll_directory(gtk_bin)
    os.environ['PATH'] = gtk_bin + os.path.pathsep + os.environ.get('PATH', '')

# 2. Tell Kivy to use Pillow ('pil'), which uses HarfBuzz/Raqm from GTK for Devanagari
os.environ['KIVY_TEXT'] = 'pil'

import threading
import re
import hashlib
import tempfile
import urllib.request
import urllib.parse
from kivy.config import Config
Config.set("graphics", "width", "400")
Config.set("graphics", "height", "800")
Config.set("graphics", "resizable", "0")

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.utils import platform

# Absolute path setup at module initialization layer
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Register fonts safely using absolute target paths
from kivy.core.text import LabelBase

LabelBase.register(
    name="NepaliFont",
    fn_regular="assets/fonts/Mukta-Regular.ttf",
    fn_bold="assets/fonts/Mukta-Regular.ttf"
)

Window.clearcolor = (0.965, 0.973, 0.949, 1)

from ui.splash import SplashScreen
from ui.home import HomeScreen
from ui.assistant import AssistantScreen
from ui.disease_screen import DiseaseScreen
from ui.weather import WeatherScreen
from ui.about import AboutScreen


class AgroSansarApp(MDApp):
    language = "ne"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"

    def build(self):
        print("🚀 Building AgroSansar (All Screens Active - Production Routing Flows)...")

        # Load structural layout definitions for all system modules
        Builder.load_file(os.path.join(BASE_DIR, "kv", "splash.kv"))
        Builder.load_file(os.path.join(BASE_DIR, "kv", "home.kv"))
        Builder.load_file(os.path.join(BASE_DIR, "kv", "assistant.kv"))
        Builder.load_file(os.path.join(BASE_DIR, "kv", "disease.kv"))
        Builder.load_file(os.path.join(BASE_DIR, "kv", "weather.kv"))
        Builder.load_file(os.path.join(BASE_DIR, "kv", "about.kv"))

        self.title = "AgroSansar"
        sm = ScreenManager()

        # Mount every viewport layer explicitly inside the ScreenManager instance
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AssistantScreen(name="assistant"))
        sm.add_widget(DiseaseScreen(name="disease"))
        sm.add_widget(WeatherScreen(name="weather"))
        sm.add_widget(AboutScreen(name="about"))

        # Boot onto splash screen safely and run native auto-transition handoffs
        sm.current = "splash"

        # Ensure audio stops cleanly when the window is closed
        Window.bind(on_request_close=self._on_window_close)
        return sm

    def _on_window_close(self, *args):
        self.stop_speaking()
        return False

    def on_stop(self):
        """Cleanly aborts all active audio/speech processes when the application closes."""
        self.stop_speaking()

    def is_speaking(self):
        """Returns True if speech is actively playing."""
        if hasattr(self, 'current_sound') and self.current_sound:
            if getattr(self.current_sound, 'state', None) == 'play':
                return True
        if hasattr(self, 'current_tts_process') and self.current_tts_process:
            if self.current_tts_process.poll() is None:
                return True
        return False

    def stop_speaking(self):
        """Immediately abort any active speech playback across desktop and mobile."""
        if hasattr(self, 'current_sound') and self.current_sound:
            try:
                self.current_sound.stop()
                self.current_sound.unload()
            except Exception:
                pass
            self.current_sound = None

        if hasattr(self, 'current_tts_process') and self.current_tts_process:
            try:
                if self.current_tts_process.poll() is None:
                    self.current_tts_process.terminate()
                    self.current_tts_process.kill()
            except Exception:
                pass
            self.current_tts_process = None

        if platform == "macosx" or sys.platform == "darwin":
            try:
                import subprocess
                subprocess.run(["pkill", "-x", "say"], capture_output=True)
            except Exception:
                pass

        if platform == "android":
            try:
                if hasattr(self, '_android_tts') and self._android_tts:
                    self._android_tts.stop()
            except Exception:
                pass
            try:
                from plyer import tts
                if hasattr(tts, 'stop'):
                    tts.stop()
            except Exception:
                pass

    def install_offline_tts_voice(self):
        """Launches Android system settings to install offline TTS voice packs."""
        if platform == "android":
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
                install_intent = Intent(TextToSpeech.Engine.ACTION_INSTALL_TTS_DATA)
                PythonActivity.mActivity.startActivity(install_intent)
            except Exception as e:
                print(f"Error launching TTS install intent: {e}")

    def _fetch_google_tts_audio(self, text, lang="ne"):
        """Fetches Google authentic neural TTS stream with local caching and chunking."""
        try:
            cache_dir = os.path.join(tempfile.gettempdir(), "agrosansar_tts")
            os.makedirs(cache_dir, exist_ok=True)
            text_hash = hashlib.md5(f"{lang}:{text}".encode("utf-8")).hexdigest()
            cache_file = os.path.join(cache_dir, f"{text_hash}.mp3")

            if os.path.exists(cache_file) and os.path.getsize(cache_file) > 1000:
                return cache_file

            # Split into chunks under 130 chars at punctuation boundaries
            sentences = re.split(r'([।\.\?\!\n,]+)', text)
            chunks = []
            curr = ""
            for s in sentences:
                if len(curr) + len(s) < 130:
                    curr += s
                else:
                    if curr.strip():
                        chunks.append(curr.strip())
                    curr = s
            if curr.strip():
                chunks.append(curr.strip())

            if not chunks:
                chunks = [text[:130]]

            combined_bytes = bytearray()
            tl = "ne" if lang == "ne" else "en"
            for chunk in chunks:
                if not chunk:
                    continue
                url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(chunk)}&tl={tl}&client=tw-ob"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                with urllib.request.urlopen(req, timeout=6) as resp:
                    combined_bytes.extend(resp.read())

            if len(combined_bytes) > 0:
                with open(cache_file, "wb") as f:
                    f.write(combined_bytes)
                return cache_file
        except Exception as e:
            print(f"⚠️ Google TTS stream fallback notice: {e}")
        return None

    def speak(self, text):
        """Global asynchronous speech engine with Google Voice fallback and native Android TTS."""
        if not text:
            return

        clean_text = re.sub(r'\[.*?\]', '', text).replace("•", "").strip()
        if not clean_text:
            return

        # 1. Stop any currently playing speech immediately before starting a new one
        self.stop_speaking()

        def _run_speech():
            played = False

            # Strategy 1: Google Voice Fallback (Primary for authentic Nepali and phones without voice data)
            audio_path = self._fetch_google_tts_audio(clean_text, self.language)
            if audio_path:
                try:
                    sound = SoundLoader.load(audio_path)
                    if sound:
                        self.current_sound = sound
                        sound.play()
                        played = True
                        return
                except Exception as err:
                    print(f"SoundLoader playback error: {err}")

            # Strategy 2: Native Android TTS with proper Nepali Locale
            if platform == "android":
                try:
                    from jnius import autoclass
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    Locale = autoclass('java.util.Locale')
                    TextToSpeech = autoclass('android.speech.tts.TextToSpeech')

                    if not hasattr(self, '_android_tts') or self._android_tts is None:
                        self._android_tts = TextToSpeech(PythonActivity.mActivity, None)

                    target_locale = Locale("ne", "NP") if self.language == "ne" else Locale.US
                    lang_status = self._android_tts.setLanguage(target_locale)

                    # lang_status: -1 is LANG_MISSING_DATA, -2 is LANG_NOT_SUPPORTED
                    if lang_status in (-1, -2):
                        print(f"Native Android TTS voice missing for {self.language} (status: {lang_status})")
                    else:
                        self._android_tts.speak(clean_text, TextToSpeech.QUEUE_FLUSH, None)
                        played = True
                        return
                except Exception as err:
                    print(f"Native Android TTS error: {err}")

            # Strategy 3: Desktop macOS 'say' command fallback
            if (platform == "macosx" or sys.platform == "darwin") and not played:
                import subprocess
                cmd = ["say", "-v", "Lekha", clean_text] if self.language == "ne" else ["say", clean_text]
                try:
                    self.current_tts_process = subprocess.Popen(cmd)
                    self.current_tts_process.wait()
                except Exception:
                    try:
                        self.current_tts_process = subprocess.Popen(["say", clean_text])
                        self.current_tts_process.wait()
                    except Exception:
                        pass
                return

            # Strategy 4: Plyer TTS generic fallback
            if not played:
                try:
                    from plyer import tts
                    tts.speak(clean_text)
                except Exception as err:
                    print(f"Plyer fallback TTS error: {err}")

        threading.Thread(target=_run_speech, daemon=True).start()


if __name__ == "__main__":
    import atexit
    atexit.register(lambda: subprocess.run(["pkill", "-x", "say"], capture_output=True) if sys.platform == "darwin" else None)
    AgroSansarApp().run()
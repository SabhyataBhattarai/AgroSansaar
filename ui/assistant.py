import threading
import re
import os
import sys
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivymd.app import MDApp
from kivy.utils import platform
import speech_recognition as sr

if platform == "android":
    from android.permissions import request_permissions, Permission
    from android import activity

translations = {
    "ne": {
        "page_title": "कृषि सहायक",
        "tagline": "तपाईंको कृषि सहयोगी",
        "answer_title": "उत्तर",
        "answer_placeholder": "तपाईंको उत्तर यहाँ देखिनेछ।",
        "question_placeholder": "तपाईंले सोध्नुभएको प्रश्न यहाँ देखिनेछ।",
        "mic_instruction": "प्रश्न सोध्न माइक्रोफोन थिच्नुहोस्",
        "suggestions_title": "उदाहरण प्रश्नहरू",
        "example1": "•  मल भनेको के हो?",
        "example2": "•  गोलभेँडामा कुन मल हाल्ने?",
        "example3": "•  गोलभेँडा कुन मौसममा लगाइन्छ?",
        "example4": "•  गोलभेँडाको पात किन पहेंलो हुन्छ?",
        "example5": "•  गोलभेँडामा रोग लागेको कसरी थाहा पाउने?"
    },
    "en": {
        "page_title": "Agriculture Assistant",
        "tagline": "Your Agriculture Assistant",
        "answer_title": "Answer",
        "answer_placeholder": "Your answer will appear here.",
        "question_placeholder": "Your question will appear here.",
        "mic_instruction": "Tap the microphone to ask a question",
        "suggestions_title": "Example Questions",
        "example1": "•  What is fertilizer?",
        "example2": "•  How do I know if my tomato plant has a disease?",
        "example3": "•  When is the best time to grow tomatoes?",
        "example4": "•  Why are my tomato leaves turning yellow?",
        "example5": "•  How much water do tomatoes need?"
    }
}


class AssistantScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bot = None
        self.language = "ne"

        if platform == "android":
            activity.bind(on_activity_result=self._on_activity_result)

    def on_enter(self):
        self.language = MDApp.get_running_app().language
        self.update_language()

        if platform == "android":
            request_permissions([Permission.RECORD_AUDIO])

    def on_leave(self):
        app = MDApp.get_running_app()
        if hasattr(app, 'stop_speaking'):
            app.stop_speaking()

    def toggle_language(self):
        self.language = "en" if self.language == "ne" else "ne"
        MDApp.get_running_app().language = self.language
        self.update_language()

    def update_language(self):
        t = translations[self.language]

        if "language_button" in self.ids:
            self.ids.language_button.text = "ने" if self.language == "en" else "EN"

        self.ids.page_title.text = t["page_title"]
        self.ids.tagline.text = t["tagline"]
        self.ids.answer_title.text = t["answer_title"]
        self.ids.mic_instruction.text = t["mic_instruction"]
        self.ids.suggestions_title.text = t["suggestions_title"]
        self.ids.example1.text = t["example1"]
        self.ids.example2.text = t["example2"]
        self.ids.example3.text = t["example3"]
        self.ids.example4.text = t["example4"]
        self.ids.example5.text = t["example5"]

        if self.ids.answer_label.text in (
            translations["ne"]["answer_placeholder"],
            translations["en"]["answer_placeholder"]
        ):
            self.ids.answer_label.text = t["answer_placeholder"]

        if self.ids.question_label.text in (
            translations["ne"]["question_placeholder"],
            translations["en"]["question_placeholder"]
        ):
            self.ids.question_label.text = t["question_placeholder"]

    def speak(self, text):
        """Passes playback responsibility seamlessly to the centralized App engine."""
        MDApp.get_running_app().speak(text)

    def listen(self):
        if self.language == "en":
            self.ids.answer_label.text = "Listening..."
        else:
            self.ids.answer_label.text = "सुन्दैछ..."

        if platform != "android":
            threading.Thread(
                target=self._listen_desktop,
                daemon=True
            ).start()
            return

        try:
            from jnius import autoclass

            Intent = autoclass('android.content.Intent')
            RecognizerIntent = autoclass('android.speech.RecognizerIntent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')

            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )

            lang_code = "en-US" if self.language == "en" else "ne-NP"
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, lang_code)
            intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            intent.putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, False)

            current_activity = PythonActivity.mActivity
            current_activity.startActivityForResult(intent, 7007)

        except Exception as e:
            print(f"Failed to trigger Jnius Android Speech Intent: {e}")
            self._handle_speech_error("generic")

    def _listen_desktop(self):
        """Desktop microphone fallback using SpeechRecognition (Google Web Speech API)."""
        recognizer = sr.Recognizer()

        try:
            with sr.Microphone() as source:
                print("🎙️ Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("🎙️ Listening on desktop mic...")
                audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)

            lang_code = "en-US" if self.language == "en" else "ne-NP"
            recognized_text = recognizer.recognize_google(audio, language=lang_code)
            print(f"✅ Desktop mic recognized: {recognized_text}")

            Clock.schedule_once(
                lambda dt: self._handle_successful_speech(recognized_text)
            )

        except sr.WaitTimeoutError:
            print("🔥 Desktop mic timeout: no speech detected")
            Clock.schedule_once(lambda dt: self._handle_speech_error("unknown"))

        except sr.UnknownValueError:
            print("🔥 Desktop mic: could not understand audio")
            Clock.schedule_once(lambda dt: self._handle_speech_error("unknown"))

        except sr.RequestError as e:
            print(f"🔥 Desktop mic: API request failed: {e}")
            Clock.schedule_once(lambda dt: self._handle_speech_error("generic"))

        except Exception as e:
            print(f"🔥 Desktop mic: unexpected error: {repr(e)}")
            Clock.schedule_once(lambda dt: self._handle_speech_error("generic"))

    def _on_activity_result(self, request_code, result_code, intent_data):
        if request_code != 7007:
            return

        from jnius import autoclass
        Activity = autoclass('android.app.Activity')

        if result_code == Activity.RESULT_OK and intent_data is not None:
            try:
                RecognizerIntent = autoclass('android.speech.RecognizerIntent')

                results = intent_data.getStringArrayListExtra(
                    RecognizerIntent.EXTRA_RESULTS
                )

                if results and results.size() > 0:
                    recognized_text = results.get(0)

                    Clock.schedule_once(
                        lambda dt: self._handle_successful_speech(recognized_text)
                    )
                else:
                    Clock.schedule_once(
                        lambda dt: self._handle_speech_error("unknown")
                    )

            except Exception as e:
                print(f"Failed parsing native string list: {e}")

                Clock.schedule_once(
                    lambda dt: self._handle_speech_error("generic")
                )

        else:
            Clock.schedule_once(
                lambda dt: self._handle_speech_error("unknown")
            )

    def select_suggestion(self, instance_label):
        clean_question = instance_label.text.replace("•", "").strip()
        self.ids.question_label.text = clean_question

        if self.language == "en":
            self.ids.answer_label.text = "Processing suggestion..."
        else:
            self.ids.answer_label.text = "प्रशोधन हुँदैछ..."

        threading.Thread(
            target=self._async_bot_response,
            args=(clean_question,),
            daemon=True
        ).start()

    def _handle_successful_speech(self, question):
        self.ids.question_label.text = question

        threading.Thread(
            target=self._async_bot_response,
            args=(question,),
            daemon=True
        ).start()

    def _async_bot_response(self, question):
        try:
            if self.bot is None:
                # Add root project folder dynamically into path mappings
                ui_dir = os.path.dirname(os.path.abspath(__file__))
                root_path = os.path.abspath(os.path.join(ui_dir, '..'))

                if root_path not in sys.path:
                    sys.path.insert(0, root_path)

                from chatbot import ChatBot
                self.bot = ChatBot()

            answer = self.bot.get_answer(question, self.language)

            Clock.schedule_once(
                lambda dt: self._update_ui_with_answer(answer)
            )

        except Exception as e:
            print(
                f"🔥 Chatbot query runner crash error trace: {repr(e)}"
            )

            error_message = f"Error: {repr(e)}"

            Clock.schedule_once(
                lambda dt: self._update_ui_with_error(
                    custom_msg=error_message
                )
            )

    def _update_ui_with_answer(self, answer):
        self.ids.answer_label.text = str(answer)
        self.speak(answer)

    def _update_ui_with_error(self, custom_msg=None):
        if custom_msg:
            msg = custom_msg
        else:
            msg = (
                "An error occurred."
                if self.language == "en"
                else "त्रुटि भयो।"
            )

        self.ids.answer_label.text = msg
        self.speak(msg)

    def _handle_speech_error(self, error_type):
        if error_type == "unknown":
            msg = (
                "Sorry, I couldn't understand your voice. Please try again."
                if self.language == "en"
                else
                "माफ गर्नुहोस्, आवाज बुझ्न सकिएन। कृपया फेरि प्रयास गर्नुहोस्।"
            )

            self.ids.answer_label.text = msg
            self.speak(msg)

        else:
            self._update_ui_with_error()
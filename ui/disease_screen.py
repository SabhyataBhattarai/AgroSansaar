import os
import sys
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.image import Image
from kivy.graphics.texture import Texture

# Lazy loading handles for asset systems
filechooser = None

# Safe conditional inclusion of custom native android camera module
try:
    import android_camera
except ImportError:
    android_camera = None


class DiseaseScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.language = "ne"

        # Desktop in-app camera state
        self.desktop_cap = None
        self.cam_event = None
        self.cam_image_widget = None
        self.current_frame = None

        if platform == "android":
            from android import activity
            activity.bind(on_activity_result=self._on_activity_result)

        Clock.schedule_once(self.request_android_permissions, 1)

    def request_android_permissions(self, *args):
        """Safely requests modern system runtime permissions asynchronously after app launch initialization."""
        if platform == "android":
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.CAMERA,
                    Permission.READ_MEDIA_IMAGES
                ])
                print("✅ Modern Android permissions requested successfully")
            except Exception as e:
                print(f"Android permissions request failed: {e}")

    #########################################################
    # SCREEN LIFE CYCLE
    #########################################################

    def on_enter(self):
        self.language = MDApp.get_running_app().language
        self.update_language()
        self.reset_result()

    def on_leave(self):
        self.stop_desktop_camera()
        app = MDApp.get_running_app()
        if hasattr(app, 'stop_speaking'):
            app.stop_speaking()

    #########################################################
    # LANGUAGE MANAGEMENT
    #########################################################

    def toggle_language(self):
        if self.language == "ne":
            self.language = "en"
        else:
            self.language = "ne"

        MDApp.get_running_app().language = self.language
        self.update_language()
        self.reset_result()

    def update_language(self):
        self.ids.language_button.text = "ने" if self.language == "en" else "EN"

        if self.language == "ne":
            self.ids.page_title.text = "रोग पहिचान"
            self.ids.tagline.text = "पातको फोटोबाट रोग पत्ता लगाउनुहोस्"
            self.ids.camera_title.text = "प्रत्यक्ष स्क्यान"
            self.ids.live_label.text = "कैमरा पूर्वावलोकन रेडी" if not self.desktop_cap else "क्यामेरा सक्रिय छ..."
            self.ids.open_camera_button.text = "क्यामेरा खोल्नुहोस्"
            self.ids.capture_button.text = "तस्वीर खिच्नुहोस्"
            self.ids.or_label.text = "वा"
            self.ids.upload_title.text = "तस्वीर अपलोड गर्नुहोस्"
            self.ids.gallery_button.text = "ग्यालरीबाट छान्नुहोस्"
            self.ids.result_heading.text = "पहिचान परिणाम"
            self.ids.treatment_heading.text = "विवरण / उपचार / रोकथाम"
        else:
            self.ids.page_title.text = "Disease Detection"
            self.ids.tagline.text = "Detect diseases from leaf images"
            self.ids.camera_title.text = "Live Scan"
            self.ids.live_label.text = "Camera Preview Ready" if not self.desktop_cap else "Camera Active..."
            self.ids.open_camera_button.text = "Open Camera"
            self.ids.capture_button.text = "Capture Image"
            self.ids.or_label.text = "OR"
            self.ids.upload_title.text = "Upload Image"
            self.ids.gallery_button.text = "Choose from Gallery"
            self.ids.result_heading.text = "Prediction Result"
            self.ids.treatment_heading.text = "Details / Treatment / Prevention"

    #########################################################
    # RESET RESULT CARD
    #########################################################

    def reset_result(self):
        self.ids.result_card.opacity = 1

        if self.language == "ne":
            self.ids.result_title.text = "अहिलेसम्म कुनै तस्बिर विश्लेषण गरिएको छैन।"
        else:
            self.ids.result_title.text = "No image has been analyzed yet."

        self.ids.result_confidence.text = ""
        self.ids.result_treatment.text = ""


    #########################################################
    # IN-APP CAMERA (Smooth 30 FPS Stream + Android Native)
    #########################################################



    def open_camera(self):
        """Launches Android intent or starts in-app desktop camera stream."""
        if android_camera and getattr(android_camera, 'IS_ANDROID', False):
            try:
                print("📸 Launching Secure Native Camera Intent...")
                android_camera.take_picture(
                    output_filename="captured_leaf.jpg",
                    on_complete_callback=self._on_native_camera_success
                )
            except Exception as e:
                print(f"❌ Native Camera Intent dispatch failure: {repr(e)}")
                self._set_camera_error_ui()
        else:
            print("🖥️ Windows detected: Starting live real-time camera stream...")
            self.stop_desktop_camera()
            self.start_desktop_camera()

    def start_desktop_camera(self):
        """Streams OpenCV camera frames smoothly inside the Kivy layout."""
        import cv2

        if sys.platform.startswith('win'):
            self.desktop_cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            self.desktop_cap = cv2.VideoCapture(0)

        if not self.desktop_cap.isOpened():
            print("❌ Could not open webcam.")
            self._set_camera_error_ui()
            self.desktop_cap = None
            return

        # Hide the last captured/uploaded photo, show the live feed
        self.ids.upload_preview.opacity = 0
        self.ids.camera_preview.opacity = 1
        self.ids.camera_preview.texture = None
        self.ids.live_label.opacity = 0

        self.cam_event = Clock.schedule_interval(self._update_desktop_camera_feed, 1.0 / 30.0)

    def _update_desktop_camera_feed(self, dt):
        """Updates Kivy Image texture on every frame to force real-time redraws."""
        if not self.desktop_cap or not self.desktop_cap.isOpened():
            return

        ret, frame = self.desktop_cap.read()
        if not ret or frame is None:
            return

        self.current_frame = frame.copy()

        import cv2
        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        self.ids.camera_preview.texture = texture

    def capture_image(self):
        """Triggered when pressing 'तस्वीर खिच्नुहोस्' (Capture Image)."""
        if android_camera and getattr(android_camera, 'IS_ANDROID', False):
            self.open_camera()
        else:
            if self.current_frame is not None:
                import cv2
                out_path = os.path.abspath("captured_leaf.jpg")
                cv2.imwrite(out_path, self.current_frame)
                print(f"✅ Live snapshot saved to: {out_path}")

                self.stop_desktop_camera()
                self._process_captured_image(out_path)
            else:
                self.open_camera()

    def stop_desktop_camera(self):
        """Stops video feed and releases webcam resource cleanly."""
        if self.cam_event:
            Clock.unschedule(self.cam_event)
            self.cam_event = None

        if self.desktop_cap:
            self.desktop_cap.release()
            self.desktop_cap = None

        if hasattr(self.ids, 'camera_preview'):
            self.ids.camera_preview.texture = None
            self.ids.camera_preview.opacity = 0

        if hasattr(self.ids, 'upload_preview'):
            self.ids.upload_preview.opacity = 1

        self.current_frame = None
        if hasattr(self.ids, 'live_label'):
            self.ids.live_label.opacity = 1

    def stop_camera(self):
        self.stop_desktop_camera()

    def _on_native_camera_success(self, resolved_file_path):
        """Callback handler executed when image is fetched on Android."""
        print(f"📸 UI Layer received native path: {resolved_file_path}")
        if resolved_file_path and os.path.exists(resolved_file_path):
            Clock.schedule_once(lambda dt: self._process_captured_image(resolved_file_path))
        else:
            print("❌ Native Camera returned invalid file pathway mapping")

    def _set_camera_error_ui(self):
        if self.language == "ne":
            self.ids.live_label.text = "क्यामेरा यो डिभाइसमा उपलब्ध छैन"
        else:
            self.ids.live_label.text = "Camera not available on this device"

    def _process_captured_image(self, filename):
        if not filename:
            return
        self.ids.upload_preview.source = str(filename)
        self.ids.upload_preview.reload()
        self.run_ai_prediction(filename)

    #########################################################
    # SYSTEM GALLERY UPLOAD (Android Intent + Desktop Tkinter Fallback)
    #########################################################

    def upload_image(self):
        """Launches Android intent picker or native file dialog on desktop."""
        try:
            from jnius import autoclass

            Intent = autoclass('android.content.Intent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')

            intent = Intent(Intent.ACTION_PICK)
            intent.setType("image/*")

            current_activity = PythonActivity.mActivity
            current_activity.startActivityForResult(intent, 9001)

        except Exception as e:
            print("🔥 Android Gallery not available. Opening Desktop File Dialog...")
            self.upload_image_desktop()

    def upload_image_desktop(self):
        """Desktop native file dialog fallback supporting macOS, Windows, and Linux."""
        try:
            file_path = None
            if platform == "macosx" or sys.platform == "darwin":
                import subprocess
                script = 'POSIX path of (choose file with prompt "Select Leaf Image" of type {"public.image"})'
                res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    file_path = res.stdout.strip()
            else:
                import tkinter as tk
                from tkinter import filedialog

                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)

                file_path = filedialog.askopenfilename(
                    title="Select Leaf Image",
                    filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp")]
                )
                root.destroy()

            if file_path:
                print(f"✅ Selected desktop file: {file_path}")
                self._process_selected_image(file_path)
        except Exception as e:
            print(f"🔥 Desktop file dialog error: {e}")

    def _on_activity_result(self, request_code, result_code, intent):
        if request_code != 9001:
            return

        try:
            if intent:
                uri = intent.getData()

                if uri:
                    path = uri.toString()
                    print("🔥 CONTENT URI:", path)

                    Clock.schedule_once(
                        lambda dt: self._process_selected_image(path)
                    )

        except Exception as e:
            print("🔥 RESULT ERROR:", repr(e))

    def _on_file_selected(self, selection):
        """Legacy fallback listener logic for Plyer engine interactions."""
        print("🔥 GALLERY RETURN:", selection)

        if not selection or selection[0] is None:
            print("⚠️ Empty selection")
            return

        selected_path = selection[0]
        print("🔥 SELECTED PATH:", selected_path)

        Clock.schedule_once(lambda dt: self._process_selected_image(selected_path))

    def _process_selected_image(self, path):
        print("🔥 PROCESSING IMAGE:", path)

        if not path:
            print("❌ Path empty")
            return

        try:
            print("🔥 FINAL IMAGE BEFORE FITIMAGE:", repr(path))

            if not isinstance(path, str):
                print("❌ PATH IS NOT STRING")
                return

            if path.strip() == "":
                print("❌ PATH EMPTY STRING")
                return

            self.ids.upload_preview.source = path
            self.ids.upload_preview.reload()

            print("✅ IMAGE LOADED INTO PREVIEW")

            self.run_ai_prediction(path)
        except Exception as e:
            print("🔥 FITIMAGE CRASH:", repr(e))

    #########################################################
    # AI MODEL INFERENCE RUNNER
    #########################################################

    def run_ai_prediction(self, image_path):
        if not image_path:
            return

        try:
            app_dir = os.path.dirname(os.path.abspath(__file__))
            root_path = os.path.abspath(os.path.join(app_dir, '..'))
            if root_path not in sys.path:
                sys.path.insert(0, root_path)
            if app_dir not in sys.path:
                sys.path.insert(0, app_dir)

            from disease.predict import predict_disease
            result = predict_disease(image_path, language=self.language)

            self.ids.result_title.text = result.get("title", "")
            self.ids.result_confidence.text = result.get("confidence", "")
            self.ids.result_treatment.text = result.get("treatment", "")
        except Exception as e:
            print(f"Error handling UI prediction updates: {e}")
            if self.language == "ne":
                self.ids.result_title.text = "त्रुटि"
                self.ids.result_treatment.text = "पहिचान प्रक्रियामा समस्या आयो।"
            else:
                self.ids.result_title.text = "Error"
                self.ids.result_treatment.text = "An error occurred during prediction processing."

    #########################################################
    # NATIVE TEXT-TO-SPEECH (TTS ALOUD)
    #########################################################

    def read_result_aloud(self):
        """Uses the global application TTS setup to vocalize output with toggle stop support."""
        app = MDApp.get_running_app()
        if hasattr(app, 'is_speaking') and app.is_speaking():
            app.stop_speaking()
            return

        title_text = self.ids.result_title.text
        details_text = self.ids.result_treatment.text

        if not details_text or "अहिलेसम्म" in title_text or "No image" in title_text:
            return

        full_speech_content = f"{title_text}. {details_text}"
        app.speak(full_speech_content)
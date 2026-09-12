from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.animation import Animation
import time


class SplashScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("🔵 SplashScreen.__init__() called")
        self.timer = None
        self.text_index = 0
        self.loading_texts = [
            "लोड हुँदै...",
            "Loading...",
            "तयार हुँदै...",
            "Almost ready..."
        ]
        self.appear_time = None
        self.animation_started = False

    def on_pre_enter(self):
        """Called BEFORE the screen is shown."""
        print("🟠 SplashScreen.on_pre_enter() called")
        if hasattr(self.ids, 'progress_bar'):
            self.ids.progress_bar.value = 0

    def on_enter(self):
        """Called AFTER the screen is shown."""
        print("🟢 SplashScreen.on_enter() called")
        self.appear_time = time.time()
        self.animation_started = False
        Clock.schedule_once(self.start_animation, 0.3)

    def start_animation(self, *args):
        """Start all animations and timers."""
        if self.animation_started:
            return
        self.animation_started = True
        
        print("🟢 Starting splash animations...")
        
        if hasattr(self.ids, 'progress_bar'):
            self.ids.progress_bar.value = 0
            anim = Animation(value=100, duration=3, t='out_quad')
            anim.start(self.ids.progress_bar)
        
        self.update_loading_text()
        
        if self.timer:
            self.timer.cancel()
        
        self.timer = Clock.schedule_once(self.go_home, 4)

    def update_loading_text(self, *args):
        """Update the loading text periodically."""
        if hasattr(self.ids, 'loading_label'):
            self.ids.loading_label.text = self.loading_texts[self.text_index % len(self.loading_texts)]
            self.text_index += 1
            if self.text_index < len(self.loading_texts):
                Clock.schedule_once(self.update_loading_text, 0.9)

    def go_home(self, *args):
        """Transitions the ScreenManager pointer automatically to the primary home layout."""
        if self.appear_time:
            elapsed = time.time() - self.appear_time
            print(f"🟡 Splash was visible for {elapsed:.2f} seconds")
            
            if elapsed < 4.0:
                wait_time = 4.0 - elapsed
                print(f"🟡 Waiting {wait_time:.2f} more seconds...")
                Clock.schedule_once(self.go_home, wait_time)
                return
        
        # RESTORED: Transition smoothly over to the home layout panel
        print("🚀 Splash window runtime finished. Handing control off to Home view...")
        if self.manager:
            self.manager.current = "home"
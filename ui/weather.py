import json
from kivy.clock import Clock  # For the GPS timeout watchdog and font initialization fix
from kivy.factory import Factory
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty
from kivy.utils import platform
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivymd.uix.menu import MDDropdownMenu

# ============================================================
# SAFE PLYER GPS IMPORT WRAPPER
# ============================================================
GPS_AVAILABLE = False
location = None

if platform == "android":
    try:
        from plyer import location
        GPS_AVAILABLE = True
    except ImportError:
        pass


# ============================================================
# CUSTOM MENU ITEM WITH BULLETPROOF RECYCLEVIEW FONT BINDING
# ============================================================
class NepaliMenuItem(OneLineListItem):
    """Custom menu item that guarantees font persistence across RecycleView updates."""
    text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = "NepaliFont"
        self.theme_text_color = "Custom"
        self.text_color = (0.145, 0.161, 0.145, 1)
        # Schedule initial font application
        Clock.schedule_once(self.apply_font, 0)

    def on_text(self, instance, value):
        """Triggers every time RecycleView updates or re-uses this item's text."""
        self.apply_font()

    def apply_font(self, *args):
        """Applies font to all possible internal sub-labels used by KivyMD list items."""
        try:
            if hasattr(self, "_lbl_primary") and self._lbl_primary:
                self._lbl_primary.font_name = "NepaliFont"
            if hasattr(self, "ids") and "label" in self.ids:
                self.ids.label.font_name = "NepaliFont"
            if hasattr(self, "ids") and "_lbl_primary" in self.ids:
                self.ids._lbl_primary.font_name = "NepaliFont"
        except Exception as e:
            print("Dropdown font bind error:", e)


# Safe Factory registration guard to prevent duplicates during hot reloads/builds
if "NepaliMenuItem" not in Factory.classes:
    Factory.register("NepaliMenuItem", cls=NepaliMenuItem)


UI_TEXT = {
    "ne": {
        "page_title": "मौसम जानकारी",
        "tagline": "तपाईंको कृषि सहयोगी",
        "day_names": ("आज", "भोलि", "पर्सि"),
        "humidity_label": "आर्द्रता",
        "wind_label": "हावा",
        "detecting": "स्थान पत्ता लगाउँदै...",
        "gps_timeout": "GPS ढिलो भयो, काठमाडौंको मौसम!",
        "api_error": "मौसम लोड हुन सकेन!",
        "perm_denied": "अनुमति अस्विकार गरियो",
    },
    "en": {
        "page_title": "Weather Information",
        "tagline": "Your Agriculture Companion",
        "day_names": ("Today", "Tomorrow", "Day After Tomorrow"),
        "humidity_label": "Humidity",
        "wind_label": "Wind",
        "detecting": "Detecting location...",
        "gps_timeout": "GPS timed out. Loading Kathmandu...",
        "api_error": "Error loading weather!",
        "perm_denied": "Permission Denied",
    },
}


class WeatherScreen(Screen):
    # Free WeatherAPI Key
    API_KEY = "8ccd400ba27344f9b30191926260907"

    city_list = [
        "Kathmandu",
        "Biratnagar",
        "Hetauda",
        "Jhapa",
        "Chitwan",
        "Nepalgunj",
        "Taplejung",
        "Solukhumbu",
    ]

    city_nepali = {
        "Kathmandu": "काठमाडौं",
        "Biratnagar": "विराटनगर",
        "Hetauda": "हेटौंडा",
        "Jhapa": "झापा",
        "Chitwan": "चितवन",
        "Nepalgunj": "नेपालगञ्ज",
        "Taplejung": "ताप्लेजुङ",
        "Solukhumbu": "सोलुखुम्बु",
    }

    weather_translation = {
        "Sunny": "घाम लागेको",
        "Clear": "सफा मौसम",
        "Cloudy": "बादल लागेको",
        "Partly cloudy": "आंशिक बदली",
        "Overcast": "घना बदली",
        "Mist": "कुहिरो",
        "Fog": "हुस्सु",
        "Patchy rain nearby": "छिटपुट वर्षा",
        "Patchy light rain": "हल्का वर्षा",
        "Light rain": "हल्का वर्षा",
        "Light rain shower": "हल्का वर्षा",
        "Moderate rain": "मध्यम वर्षा",
        "Moderate rain at times": "मध्यम वर्षा",
        "Heavy rain": "भारी वर्षा",
        "Heavy rain at times": "भारी वर्षा",
        "Heavy rain shower": "भारी वर्षा",
        "Thundery outbreaks possible": "चट्याङको सम्भावना",
        "Thunderstorm": "चट्याङसहित वर्षा",
        "Patchy snow nearby": "हिउँ पर्ने सम्भावना",
        "Light snow": "हल्का हिमपात",
        "Heavy snow": "भारी हिमपात",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu = None
        self.current_city = "Kathmandu"
        self.language = "ne"
        self.gps_started = False
        self.gps_timer = None

    def on_enter(self):
        self.language = MDApp.get_running_app().language
        self.update_language()
        self.build_city_menu()
        self.ids.city_spinner.text = self.get_city_display("Kathmandu")
        self.load_weather("Kathmandu")

    def build_city_menu(self):
        """Build the dropdown menu styled to exactly match the 150dp pill width."""
        menu_items = []
        for city in self.city_list:
            menu_items.append(
                {
                    "viewclass": "NepaliMenuItem",
                    "text": self.get_city_display(city),
                    "on_release": lambda x=city: self.menu_callback(x),
                }
            )

        self.menu = MDDropdownMenu(
            caller=self.ids.city_pill,
            items=menu_items,
            width=dp(150),
            max_height=dp(250),
            position="bottom"
        )

    def open_city_menu(self):
        """Tears down and recreates the menu to guarantee clean layout rendering."""
        if self.menu:
            self.menu.dismiss()
        self.build_city_menu()
        self.menu.open()

    def menu_callback(self, city):
        if self.menu:
            self.menu.dismiss()
        self.select_city(city)

    def use_live_location(self):
        """Triggers GPS logic, handles Android permission, and runs desktop fallback."""
        if platform == "android":
            from android.permissions import Permission, request_permissions

            def permission_callback(permissions, grants):
                if all(grants):
                    self.start_gps_tracking()
                else:
                    self.ids.city_spinner.text = UI_TEXT[self.language]["perm_denied"]
                    Clock.schedule_once(lambda x: self.load_weather("Kathmandu"), 1.5)

            request_permissions(
                [Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION],
                permission_callback,
            )
        else:
            if not GPS_AVAILABLE:
                print("GPS unavailable on desktop. Fallback to Kathmandu.")
                self.load_weather("Kathmandu")
            else:
                self.start_gps_tracking()

    def start_gps_tracking(self):
        """Configures Plyer location tracking with a safety timeout callback."""
        t = UI_TEXT[self.language]
        self.ids.city_spinner.text = t["detecting"]

        if self.gps_timer:
            Clock.unschedule(self.gps_timer)

        self.gps_timer = Clock.schedule_once(self.gps_timeout_handler, 15)

        try:
            location.configure(
                on_location=self.on_gps_location,
                on_status=self.on_gps_status
            )
            location.start(minTime=5000, minDistance=10)
            self.gps_started = True
        except Exception as e:
            print("GPS Start Error:", e)
            self.cancel_gps_watchdog()
            self.load_weather("Kathmandu")

    def on_gps_location(self, **kwargs):
        lat = kwargs.get("lat")
        lon = kwargs.get("lon")

        if lat is not None and lon is not None:
            print(f"GPS Located: {lat}, {lon}")
            self.stop_gps_engine()
            self.load_weather(f"{lat},{lon}")

    def gps_timeout_handler(self, dt):
        """Called when the phone fails to retrieve a GPS lock in 15 seconds."""
        if self.gps_started:
            print("GPS timed out. Stopping engine and dropping to default...")
            self.stop_gps_engine()
            self.ids.city_spinner.text = UI_TEXT[self.language]["gps_timeout"]
            Clock.schedule_once(lambda x: self.load_weather("Kathmandu"), 1.5)

    def stop_gps_engine(self):
        """Safely tears down the hardware location engine."""
        self.cancel_gps_watchdog()
        try:
            if GPS_AVAILABLE and location:
                location.stop()
        except Exception as e:
            print("Error turning off GPS:", e)
        self.gps_started = False

    def cancel_gps_watchdog(self):
        if self.gps_timer:
            Clock.unschedule(self.gps_timer)
            self.gps_timer = None

    def on_gps_status(self, stype, status):
        print("GPS status:", stype, status)

    def toggle_language(self):
        self.language = "en" if self.language == "ne" else "ne"
        MDApp.get_running_app().language = self.language

        if self.menu:
            self.menu.dismiss()

        self.build_city_menu()
        self.update_language()
        self.load_weather(self.current_city)

    def update_language(self):
        self.ids.language_button.text = "ने" if self.language == "en" else "EN"
        t = UI_TEXT[self.language]
        self.ids.page_title.text = t["page_title"]
        self.ids.tagline.text = t["tagline"]

        if self.current_city:
            self.ids.city_spinner.text = self.get_city_display(self.current_city)

    def get_city_display(self, city):
        if "," in city:
            return city
        if self.language == "ne":
            return self.city_nepali.get(city, city)
        return city

    def select_city(self, city):
        self.current_city = city
        self.ids.city_spinner.text = self.get_city_display(city)
        self.load_weather(city)

    def load_weather(self, city):
        url = (
            f"https://api.weatherapi.com/v1/forecast.json"
            f"?key={self.API_KEY}"
            f"&q={city}"
            f"&days=3"
            f"&aqi=no"
            f"&alerts=no"
        )

        UrlRequest(
            url,
            on_success=lambda req, result: self.on_weather_success(result, city),
            on_failure=lambda req, result: self.on_weather_error(result, city),
            on_error=lambda req, error: self.on_weather_error(error, city),
            timeout=10
        )

    def on_weather_success(self, response, requested_city):
        if "forecast" not in response:
            print(f"Invalid API response structure: {response}")
            self.on_weather_error(response, requested_city)
            return

        resolved_city = response.get("location", {}).get("name", requested_city)
        self.current_city = resolved_city
        self.ids.city_spinner.text = self.get_city_display(resolved_city)

        forecast = response["forecast"]["forecastday"]
        day_names = UI_TEXT[self.language]["day_names"]

        self.update_card(self.ids.day1, forecast[0], day_names[0])
        self.update_card(self.ids.day2, forecast[1], day_names[1])
        self.update_card(self.ids.day3, forecast[2], day_names[2])

    def on_weather_error(self, error, requested_city):
        print(f"Weather request failed: {error}")
        self.ids.city_spinner.text = UI_TEXT[self.language]["api_error"]
        if requested_city != "Kathmandu":
            Clock.schedule_once(lambda x: self.load_weather("Kathmandu"), 2)

    def update_card(self, card, data, title):
        day = data["day"]
        t = UI_TEXT[self.language]

        if self.language == "ne":
            condition = self.weather_translation.get(
                day["condition"]["text"],
                day["condition"]["text"]
            )
        else:
            condition = day["condition"]["text"]

        card.ids.title.text = title
        card.ids.temp.text = f"{round(day['avgtemp_c'])} °C"
        card.ids.condition.text = condition
        card.ids.humidity.text = f"{t['humidity_label']} : {round(day['avghumidity'])}%"
        card.ids.wind.text = f"{t['wind_label']} : {round(day['maxwind_kph'])} km/h"
        card.ids.icon.source = "https:" + day["condition"]["icon"]
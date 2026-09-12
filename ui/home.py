import datetime

from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from translations import translations


# =====================================================================
# Daily farming tip pool (bilingual).
# A tip is picked automatically based on the day of the year, so it
# changes once every 24 hours without needing an internet connection.
# Feel free to add/edit/reorder tips freely — just keep the "ne" and
# "en" lists the same length and in matching order (index i in "ne"
# should be the translation of index i in "en").
# =====================================================================
DAILY_TIPS = {
    "ne": [
        "स्वस्थ बालीका लागि हरेक हप्ता माटोको आर्द्रता जाँच गर्नुहोस्।",
        "बिउ रोप्नुअघि माटोको pH स्तर जाँच गर्नुहोस्।",
        "फसल घुमाउँदा माटोको उर्वराशक्ति कायम रहन्छ।",
        "बिहान चाँडै वा साँझ सिँचाइ गर्दा पानीको वाष्पीकरण कम हुन्छ।",
        "कम्पोष्ट प्रयोग गर्दा रासायनिक मलको आवश्यकता घट्छ।",
        "बालीको पातमा पहेँलोपन देखिए तुरुन्तै नाइट्रोजन जाँच गर्नुहोस्।",
        "अत्यधिक सिँचाइले जरा कुहिने समस्या ल्याउन सक्छ।",
        "मल्चिङ (माटो छोप्ने) ले माटोको आर्द्रता र भाइरस दुबै नियन्त्रण गर्छ।",
        "किटनाशक प्रयोग गर्नुअघि सधैं लेबल पढ्नुहोस्।",
        "स्वस्थ बिउ छनोट गर्दा उत्पादन बढ्छ।",
        "बाली कटानीपछि माटोमा जैविक मल मिसाउनुहोस्।",
        "धेरै बिरुवा एकै ठाउँमा नरोप्नुहोस्, हावा-पानीको आवतजावत चाहिन्छ।",
        "साथी बाली (companion planting) ले किरा नियन्त्रणमा मद्दत गर्छ।",
        "वर्षा हुनुभन्दा पहिले रासायनिक छर्काइ नगर्नुहोस्।",
        "झारपात समयमै हटाउँदा बालीले राम्रो पोषण पाउँछ।",
        "गमला वा बेडमा जल निकासको राम्रो व्यवस्था गर्नुहोस्।",
        "गर्मीमा दिउँसो सिँचाइ गर्दा पातमा डढेको दाग पर्न सक्छ।",
        "बीउ भण्डारण गर्दा सुख्खा र ठण्डा ठाउँमा राख्नुहोस्।",
        "माटो परीक्षण वर्षको एक पटक गर्नु राम्रो अभ्यास हो।",
        "जैविक कीटनाशकले माटोको स्वास्थ्य लामो समयसम्म कायम राख्छ।",
    ],
    "en": [
        "Check soil moisture weekly for healthier crops.",
        "Test your soil's pH level before planting seeds.",
        "Crop rotation helps keep the soil fertile over time.",
        "Watering early morning or evening reduces water loss to evaporation.",
        "Using compost reduces your need for chemical fertilizer.",
        "Yellowing leaves are often an early sign of nitrogen deficiency.",
        "Overwatering can cause root rot — water only as needed.",
        "Mulching helps retain soil moisture and suppress weeds.",
        "Always read the label before applying any pesticide.",
        "Choosing healthy, disease-free seeds improves yield.",
        "Mix organic manure into the soil after harvest.",
        "Avoid overcrowding plants — they need airflow and light.",
        "Companion planting can naturally help control pests.",
        "Avoid spraying chemicals right before expected rainfall.",
        "Removing weeds early helps crops get more nutrients.",
        "Make sure beds and pots have good drainage.",
        "Midday watering in hot weather can scorch leaves.",
        "Store seeds in a cool, dry place to keep them viable.",
        "Testing your soil once a year is a good habit.",
        "Organic pesticides help preserve long-term soil health.",
    ],
}


class HomeScreen(Screen):

    language = "ne"

    def on_enter(self):

        # NEW: read the global language instead of always resetting to "ne"
        self.language = MDApp.get_running_app().language

        self.update_language()

    def toggle_language(self):

        if self.language == "ne":
            self.language = "en"
        else:
            self.language = "ne"

        # NEW: push the change to the app-wide language so every other
        # screen picks it up automatically on their next on_enter
        MDApp.get_running_app().language = self.language

        self.update_language()

    def update_language(self):

        t = translations[self.language]

        self.ids.tagline.text = t["tagline"]

        self.ids.assistant_title.text = t["assistant_title"]
        self.ids.assistant_subtitle.text = t["assistant_subtitle"]

        self.ids.disease_title.text = t["disease_title"]
        self.ids.disease_subtitle.text = t["disease_subtitle"]

        self.ids.weather_title.text = t["weather_title"]
        self.ids.weather_subtitle.text = t["weather_subtitle"]

        self.ids.about_title.text = t["about_title"]
        self.ids.about_subtitle.text = t["about_subtitle"]

        self.ids.language_button.text = t["button"]

        # daily tip, refreshed on every language toggle / screen entry
        self.ids.tip_title.text = "आजको सुझाव" if self.language == "ne" else "Tip of the Day"
        self.ids.tip_label.text = self.get_daily_tip()

    # picks a tip based on the current day of the year, so it
    # automatically changes once every 24 hours.
    def get_daily_tip(self):

        tips = DAILY_TIPS[self.language]

        day_index = datetime.date.today().timetuple().tm_yday

        return tips[day_index % len(tips)]

    def open_assistant(self):
        self.manager.current = "assistant"

    def open_disease(self):
        self.manager.current = "disease"

    def open_weather(self):
        self.manager.current = "weather"

    def open_about(self):
        self.manager.current = "about"

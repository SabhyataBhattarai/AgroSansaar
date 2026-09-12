from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp


class AboutScreen(Screen):

    def on_enter(self):
        # Read the global language instead of always resetting to "ne"
        self.language = MDApp.get_running_app().language
        self.update_language()

    def toggle_language(self):
        if self.language == "ne":
            self.language = "en"
        else:
            self.language = "ne"

        # Push the change to the app-wide language so every other screen picks it up
        MDApp.get_running_app().language = self.language
        self.update_language()

    def update_language(self):
        # Update language flag button string
        self.ids.language_button.text = "ने" if self.language == "en" else "EN"

        if self.language == "ne":
            self.ids.page_title.text = "हाम्रो बारेमा"
            self.ids.tagline.text = "तपाईंको कृषि सहयोगी"

            self.ids.description.text = (
                "AgroSansar नेपाली किसानका लागि तयार गरिएको कृषि सहायक मोबाइल अनुप्रयोग हो। "
                "यसले कृषि सम्बन्धी प्रश्नहरूको उत्तर दिन्छ, मौसमको जानकारी उपलब्ध गराउँछ तथा "
                "गोलभेँडाको रोग पहिचान गर्न सहयोग गर्दछ।"
            )

            self.ids.objective_title.text = "हाम्रो उद्देश्य"

            # Clean, safe, standard text bullet points
            self.ids.objective1.text = "•  नेपाली भाषामा कृषि जानकारी"
            self.ids.objective2.text = "•  कृषि सम्बन्धी प्रश्नहरूको उत्तर"
            self.ids.objective3.text = "•  मौसम सम्बन्धी जानकारी"
            self.ids.objective4.text = "•  बाली रोग पहिचान"
            self.ids.objective5.text = "•  आधुनिक कृषि प्रविधिमा सहयोग"

            self.ids.developers_title.text = "विकासकर्ता"
            self.ids.developer1.text = "सभ्यता भट्टराई"
            self.ids.developer2.text = "आयुष्मा गौतम"

            self.ids.course.text = "बीसीए अन्तिम वर्ष"
            self.ids.university.text = "त्रिभुवन विश्वविद्यालय"

        else:
            self.ids.page_title.text = "About"
            self.ids.tagline.text = "Your Agriculture Companion"

            self.ids.description.text = (
                "AgroSansar is a smart agriculture assistant developed for Nepali farmers. "
                "It answers agriculture-related questions, provides weather information, "
                "and helps identify tomato plant diseases."
            )

            self.ids.objective_title.text = "Our Objectives"

            # Match English layout smoothly with the same safe bullets
            self.ids.objective1.text = "•  Agriculture information in Nepali"
            self.ids.objective2.text = "•  Answer agriculture questions"
            self.ids.objective3.text = "•  Weather information"
            self.ids.objective4.text = "•  Crop disease detection"
            self.ids.objective5.text = "•  Support modern farming"

            self.ids.developers_title.text = "Developers"
            self.ids.developer1.text = "Sabhyata Bhattarai"
            self.ids.developer2.text = "Aayushma Gautam"

            self.ids.course.text = "Final Year BCA"
            self.ids.university.text = "Tribhuvan University"
import os
import re
import csv
from rapidfuzz import fuzz
from kivy.app import App

class ChatBot:
    def __init__(self):
        # Dynamically discover local root paths correctly across desktop environments and mobile APK builds
        app = App.get_running_app()
        if app and hasattr(app, 'directory') and app.directory:
            base_path = app.directory
        else:
            base_path = os.path.abspath(os.path.dirname(__file__))

        nepali_csv = os.path.join(base_path, "assets", "dataset", "nepali_dataset.csv")
        english_csv = os.path.join(base_path, "assets", "dataset", "english_dataset.csv")

        print(f"🔍 ChatBot is loading datasets via built-in CSV module from: {base_path}")
        
        try:
            self.nepali = self._load_and_normalize(nepali_csv, "Nepali dataset")
        except Exception as e:
            print(f"🔥 Failed to load Nepali Dataset at {nepali_csv}: {e}")
            raise e

        try:
            self.english = self._load_and_normalize(english_csv, "English dataset")
        except Exception as e:
            print(f"🔥 Failed to load English Dataset at {english_csv}: {e}")
            raise e

    def _load_and_normalize(self, file_path, label):
        """Loads the CSV file and normalizes headers to standard 'question' and 'answer' keys."""
        normalized_data = []
        
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            raw_fieldnames = reader.fieldnames if reader.fieldnames else []
            print(f"{label} raw columns:", raw_fieldnames)
            
            # Map raw column names to standardized 'question' and 'answer' keys
            rename_map = {}
            for col in raw_fieldnames:
                key = col.strip().lower()
                if "question" in key:
                    rename_map[col] = "question"
                elif "answer" in key:
                    rename_map[col] = "answer"

            if "question" not in rename_map.values() or "answer" not in rename_map.values():
                print(f"WARNING: {label} is missing standard headers.")

            # Rebuild row dictionaries using the normalized keys
            for row in reader:
                normalized_row = {}
                for raw_key, value in row.items():
                    norm_key = rename_map.get(raw_key, raw_key)
                    normalized_row[norm_key] = value
                normalized_data.append(normalized_row)
                
        return normalized_data

    def clean(self, text):
        if not text:
            return ""
        text = str(text).lower()
        text = re.sub(r"[^\w\s\u0900-\u097F]", " ", text)
        text = " ".join(text.split())

        replacements = {
            "tomatoes": "tomato", "plants": "plant", "leaves": "leaf", "leafs": "leaf",
            "fertilisers": "fertilizer", "watering": "water", "गोलभेँडाको": "गोलभेँडा",
            "गोलभेँडामा": "गोलभेँडा", "गोलभेँडालाई": "गोलभेँडा", "बिरुवामा": "बिरुवा",
            "बिरुवाको": "बिरुवा", "पातहरू": "पात", "पातहरु": "पात", "कहिले": "समय"
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def get_answer(self, question, language="ne"):
        if language == "en":
            dataset = self.english
            fallback = "Sorry, I couldn't understand your question."
        else:
            dataset = self.nepali
            fallback = "माफ गर्नुहोस्, मैले तपाईंको प्रश्न बुझिनँ।"

        question = self.clean(question)
        best_score, best_answer = -1, fallback

        for row in dataset:
            # Safely get keys checking for missing or null entries
            q_text = row.get("question")
            a_text = row.get("answer")
            
            if not q_text or not a_text:
                continue
                
            dataset_question = self.clean(q_text)
            score = fuzz.WRatio(question, dataset_question)
            if score > best_score:
                best_score = score
                best_answer = a_text

        if best_score >= 88:
            return best_answer
        return fallback
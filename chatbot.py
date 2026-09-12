import os
import re
import csv
import math
import collections
from rapidfuzz import fuzz
from kivy.app import App

STOP_WORDS = {
    "ne": {
        'के', 'हो', 'छ', 'र', 'मा', 'को', 'का', 'की', 'लाई', 'बाट', 'त',
        'पनि', 'भनेको', 'कसरी', 'किन', 'कहिले', 'कुन', 'चाहिन्छ', 'गर्ने',
        'हुन्छ', 'छन्', 'गर्छ', 'गर्न', 'लागि', 'हुन', 'म', 'हामी'
    },
    "en": {
        'what', 'is', 'are', 'the', 'a', 'an', 'to', 'how', 'when', 'why',
        'in', 'on', 'for', 'of', 'and', 'do', 'does', 'should', 'can',
        'i', 'you', 'my', 'your', 'about', 'with', 'at', 'be'
    }
}


class TfidfEngine:
    """
    Level 1 Statistical NLP: In-Memory TF-IDF Vector Space Model & Cosine Similarity.
    Features unigrams, bigrams, subword smoothing, and Devanagari normalization.
    """
    def __init__(self, documents, language="ne"):
        self.language = language
        self.documents = documents
        self.stopwords = STOP_WORDS.get(language, STOP_WORDS["ne"])
        self.vocab = {}
        self.idf = {}
        self.doc_vectors = []
        self._build_index()

    def normalize(self, text):
        if not text:
            return ""
        text = str(text).lower()
        text = re.sub(r"[^\w\s\u0900-\u097F]", " ", text)
        text = text.replace("ँ", "")  # Strip chandrabindu for unified matching
        text = text.replace("टमाटर", "गोलभेडा")
        clean = " ".join(text.split())

        if self.language == "en":
            clean = re.sub(r"\btomatoes\b", "tomato", clean)
            clean = re.sub(r"\b(planting|planted)\b", "grow", clean)
            clean = re.sub(r"\bplants\b", "plant", clean)
            clean = re.sub(r"\b(fertilisers|fertilizers|fertilizing)\b", "fertilizer", clean)
            clean = re.sub(r"\b(watering|watered)\b", "water", clean)
            clean = re.sub(r"\b(leaves|leafs)\b", "leaf", clean)
        else:
            clean = re.sub(r"\b(गोलभेडामा|गोलभेडाको|गोलभेडालाई)\b", "गोलभेडा", clean)
            clean = re.sub(r"\b(बिरुवामा|बिरुवाको|बिरुवालाई)\b", "बिरुवा", clean)
            clean = re.sub(r"\b(पातमा|पातको|पातहरू|पातहरु)\b", "पात", clean)
            clean = re.sub(r"\b(माटोमा|माटोको)\b", "माटो", clean)
            clean = re.sub(r"\b(बालीमा|बालीको)\b", "बाली", clean)
            clean = re.sub(r"\b(लाग्ने|लागेको|लाग्छ|लागेमा)\b", "लाग", clean)

        return clean

    def tokenize(self, text):
        clean = self.normalize(text)
        if not clean:
            return []
        raw_words = [w for w in clean.split() if w]
        filtered_words = [w for w in raw_words if w not in self.stopwords]
        base_words = filtered_words if filtered_words else raw_words

        tokens = list(base_words)
        # Add bigrams for adjacent context awareness
        for i in range(len(base_words) - 1):
            tokens.append(f"{base_words[i]} {base_words[i+1]}")
        return tokens

    def _build_index(self):
        self.vocab = {}
        doc_tokens_list = []
        doc_freq = collections.defaultdict(int)
        n_docs = len(self.documents)

        for doc in self.documents:
            q_text = doc.get("question", "")
            tokens = self.tokenize(q_text)
            doc_tokens_list.append(tokens)
            for token in set(tokens):
                if token not in self.vocab:
                    self.vocab[token] = len(self.vocab)
                doc_freq[token] += 1

        self.idf = {}
        for term, term_idx in self.vocab.items():
            df = doc_freq[term]
            # Smooth IDF: ln((1 + N) / (1 + df)) + 1
            self.idf[term] = math.log((1 + n_docs) / (1 + df)) + 1.0

        self.doc_vectors = [self._vectorize(tokens) for tokens in doc_tokens_list]

    def _vectorize(self, tokens):
        if not tokens:
            return {}
        counts = collections.Counter(tokens)
        vec = {}
        sum_sq = 0.0
        n_tokens = len(tokens)

        for term, count in counts.items():
            if term in self.vocab:
                tf = count / n_tokens
                tfidf = tf * self.idf[term]
                vec[term] = tfidf
                sum_sq += tfidf * tfidf

        # L2 Unit Normalization
        norm = math.sqrt(sum_sq) or 1.0
        return {term: val / norm for term, val in vec.items()}

    def search(self, query):
        q_tokens = self.tokenize(query)
        q_vec = self._vectorize(q_tokens)
        if not q_vec:
            return []

        results = []
        for idx, doc_vec in enumerate(self.doc_vectors):
            score = 0.0
            for term, q_val in q_vec.items():
                if term in doc_vec:
                    score += q_val * doc_vec[term]
            results.append((score, idx))

        results.sort(key=lambda x: x[0], reverse=True)
        return results


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
            self.nepali_engine = TfidfEngine(self.nepali, language="ne")
        except Exception as e:
            print(f"🔥 Failed to load Nepali Dataset at {nepali_csv}: {e}")
            raise e

        try:
            self.english = self._load_and_normalize(english_csv, "English dataset")
            self.english_engine = TfidfEngine(self.english, language="en")
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

            rename_map = {}
            for col in raw_fieldnames:
                key = col.strip().lower()
                if "question" in key:
                    rename_map[col] = "question"
                elif "answer" in key:
                    rename_map[col] = "answer"

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
            engine = self.english_engine
            dataset = self.english
            fallback = "Sorry, I couldn't understand your question."
        else:
            engine = self.nepali_engine
            dataset = self.nepali
            fallback = "माफ गर्नुहोस्, मैले तपाईंको प्रश्न बुझिनँ।"

        # 1. Statistical NLP: TF-IDF Vector Space Model & Cosine Similarity
        nlp_results = engine.search(question)
        if nlp_results and nlp_results[0][0] >= 0.35:
            best_idx = nlp_results[0][1]
            return dataset[best_idx].get("answer", fallback)

        # 2. Secondary Fallback: Levenshtein distance for speech/typing typos
        clean_q = self.clean(question)
        best_score, best_answer = -1, fallback

        for row in dataset:
            q_text = row.get("question")
            a_text = row.get("answer")
            if not q_text or not a_text:
                continue

            dataset_question = self.clean(q_text)
            score = fuzz.WRatio(clean_q, dataset_question)
            if score > best_score:
                best_score = score
                best_answer = a_text

        if best_score >= 82:
            return best_answer

        return fallback
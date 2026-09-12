/**
 * AgroSansar NLP Engine: Level 1 Statistical NLP (TF-IDF Vector Space Model + Cosine Similarity)
 * 
 * Features:
 * 1. Multilingual Tokenization (Devanagari & English)
 * 2. Unigrams + Bigrams for context awareness (e.g. "मल हाल्ने", "फौजी कीरा")
 * 3. Domain Stop-Word Filtering
 * 4. Inverse Document Frequency (IDF) Matrix
 * 5. L2-Normalized Vector Space Representation
 * 6. High-Performance In-Memory Cosine Similarity
 */

const STOP_WORDS = {
  ne: new Set([
    'के', 'हो', 'छ', 'र', 'मा', 'को', 'का', 'की', 'लाई', 'बाट', 'त',
    'पनि', 'भनेको', 'कसरी', 'किन', 'कहिले', 'कुन', 'चाहिन्छ', 'गर्ने',
    'हुन्छ', 'छन्', 'गर्छ', 'गर्न', 'लागि', 'हुन', 'म', 'हामी'
  ]),
  en: new Set([
    'what', 'is', 'are', 'the', 'a', 'an', 'to', 'how', 'when', 'why',
    'in', 'on', 'for', 'of', 'and', 'do', 'does', 'should', 'can',
    'i', 'you', 'my', 'your', 'about', 'with', 'at', 'be'
  ])
};

export class TfidfEngine {
  constructor(documents = [], language = 'ne') {
    this.language = language;
    this.documents = documents; // array of { question, answer }
    this.stopWords = STOP_WORDS[language] || STOP_WORDS.ne;
    this.vocabulary = new Map(); // term -> index
    this.idf = []; // index -> idf score
    this.docVectors = []; // index -> { [termIdx]: weight }

    if (documents.length > 0) {
      this.buildIndex();
    }
  }

  /**
   * Cleans text and unifies Devanagari variations & English morphology
   */
  normalize(text) {
    if (!text) return '';
    let clean = text
      .toLowerCase()
      .replace(/[•\?\!\,\।\.\:\;\"\']/g, ' ')
      .replace(/ँ/g, '') // Strip chandrabindu for unified matching
      .replace(/टमाटर/g, 'गोलभेडा')
      .replace(/\s+/g, ' ')
      .trim();

    if (this.language === 'en') {
      clean = clean
        .replace(/\btomatoes\b/g, 'tomato')
        .replace(/\b(planting|planted)\b/g, 'grow')
        .replace(/\bplants\b/g, 'plant')
        .replace(/\b(fertilisers|fertilizers|fertilizing)\b/g, 'fertilizer')
        .replace(/\b(watering|watered)\b/g, 'water')
        .replace(/\b(leaves|leafs)\b/g, 'leaf');
    } else {
      // Nepali postposition and verb normalization
      clean = clean
        .replace(/\b(गोलभेडामा|गोलभेडाको|गोलभेडालाई)\b/g, 'गोलभेडा')
        .replace(/\b(बिरुवामा|बिरुवाको|बिरुवालाई)\b/g, 'बिरुवा')
        .replace(/\b(पातमा|पातको|पातहरू|पातहरु)\b/g, 'पात')
        .replace(/\b(माटोमा|माटोको)\b/g, 'माटो')
        .replace(/\b(बालीमा|बालीको)\b/g, 'बाली')
        .replace(/\b(लाग्ने|लागेको|लाग्छ|लागेमा)\b/g, 'लाग');
    }

    return clean;
  }

  /**
   * Tokenizes text into unigrams and bigrams
   */
  tokenize(text) {
    const clean = this.normalize(text);
    if (!clean) return [];

    const rawWords = clean.split(' ').filter((w) => w.length > 0);
    const filteredWords = rawWords.filter((w) => !this.stopWords.has(w));

    // Fallback: if all words were stopwords (e.g. "के हो?"), keep raw words
    const baseWords = filteredWords.length > 0 ? filteredWords : rawWords;

    const tokens = [...baseWords];

    // Add bigrams if more than 1 word exists
    for (let i = 0; i < baseWords.length - 1; i++) {
      tokens.push(`${baseWords[i]} ${baseWords[i + 1]}`);
    }

    return tokens;
  }

  /**
   * Builds the TF-IDF Matrix and precomputes L2-normalized document vectors
   */
  buildIndex() {
    this.vocabulary.clear();
    const docTokensList = [];
    const docFrequency = new Map(); // term -> count of documents containing term
    const numDocs = this.documents.length;

    // 1. Tokenize all questions & collect document frequencies
    this.documents.forEach((doc, docIdx) => {
      const tokens = this.tokenize(doc.question);
      docTokensList.push(tokens);

      const uniqueTokens = new Set(tokens);
      uniqueTokens.forEach((token) => {
        if (!this.vocabulary.has(token)) {
          this.vocabulary.set(token, this.vocabulary.size);
        }
        docFrequency.set(token, (docFrequency.get(token) || 0) + 1);
      });
    });

    // 2. Compute Inverse Document Frequency (IDF) with smoothing
    const vocabSize = this.vocabulary.size;
    this.idf = new Float32Array(vocabSize);

    this.vocabulary.forEach((termIdx, term) => {
      const df = docFrequency.get(term) || 1;
      // Smooth IDF formula: ln((1 + N) / (1 + df)) + 1
      this.idf[termIdx] = Math.log((1 + numDocs) / (1 + df)) + 1.0;
    });

    // 3. Vectorize every document & apply L2 normalization
    this.docVectors = docTokensList.map((tokens) => {
      return this.vectorizeTokens(tokens);
    });
  }

  /**
   * Converts token array into a sparse, L2-normalized TF-IDF vector
   */
  vectorizeTokens(tokens) {
    if (tokens.length === 0) return { indices: [], values: [] };

    // Compute Term Frequency (TF)
    const tfCounts = new Map();
    tokens.forEach((t) => {
      tfCounts.set(t, (tfCounts.get(t) || 0) + 1);
    });

    const indices = [];
    const values = [];
    let sumSquares = 0;

    tfCounts.forEach((count, term) => {
      if (this.vocabulary.has(term)) {
        const termIdx = this.vocabulary.get(term);
        const tf = count / tokens.length;
        const tfidf = tf * this.idf[termIdx];

        indices.push(termIdx);
        values.push(tfidf);
        sumSquares += tfidf * tfidf;
      }
    });

    // L2 Unit Normalization: ||v|| = 1
    const l2Norm = Math.sqrt(sumSquares) || 1.0;
    const normalizedValues = values.map((v) => v / l2Norm);

    return { indices, values: normalizedValues };
  }

  /**
   * Computes the Cosine Similarity between two L2-normalized sparse vectors
   * Because both vectors have ||v|| = 1, Cosine(u, v) = dot_product(u, v)
   */
  cosineSimilarity(vecA, vecB) {
    if (vecA.indices.length === 0 || vecB.indices.length === 0) return 0;

    let dotProduct = 0;
    let i = 0;
    let j = 0;

    // Linear merge scan over sorted indices
    while (i < vecA.indices.length && j < vecB.indices.length) {
      if (vecA.indices[i] === vecB.indices[j]) {
        dotProduct += vecA.values[i] * vecB.values[j];
        i++;
        j++;
      } else if (vecA.indices[i] < vecB.indices[j]) {
        i++;
      } else {
        j++;
      }
    }

    return dotProduct;
  }

  /**
   * Queries the engine and returns ranked matches sorted by cosine similarity
   */
  search(query, topK = 5) {
    const queryTokens = this.tokenize(query);
    const queryVec = this.vectorizeTokens(queryTokens);

    if (queryVec.indices.length === 0) {
      return [];
    }

    const scoredResults = this.documents.map((doc, idx) => {
      const sim = this.cosineSimilarity(queryVec, this.docVectors[idx]);
      return {
        item: doc,
        score: sim, // Cosine score between 0.0 and 1.0
        index: idx
      };
    });

    // Sort descending by similarity score
    scoredResults.sort((a, b) => b.score - a.score);

    return scoredResults.slice(0, topK);
  }
}

# app.py
from flask import Flask, render_template, request, jsonify
from keybert import KeyBERT
import yake
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords

app = Flask(__name__)

# Download NLTK data
nltk.download('stopwords')

# Initialize models
kw_model = KeyBERT()
yake_extractor = yake.KeywordExtractor(lan="en", n=2, dedupLim=0.9, top=10)
stop_words = set(stopwords.words("english"))


def generate_hashtags(text):
    # Extract keywords using KeyBERT
    keybert_keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2),
                                                 stop_words="english", top_n=10)
    keybert_hashtags = {kw[0].replace(" ", "") for kw in keybert_keywords}

    # Extract keywords using YAKE
    yake_keywords = {kw[0].replace(" ", "") for kw in yake_extractor.extract_keywords(text)}

    # Extract keywords using TF-IDF
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform([text])
    tfidf_keywords = {word.replace(" ", "") for word in vectorizer.get_feature_names_out()[:10]}

    # Merge all keywords and remove duplicates
    all_keywords = keybert_hashtags.union(yake_keywords, tfidf_keywords)
    all_keywords = [f"#{word}" for word in all_keywords if word.lower() not in stop_words]

    return all_keywords[:10]  # Limit to top 10 hashtags


@app.route('/')
def index():
    return render_template('hashtag.html')


@app.route('/generate', methods=['POST'])
def generate():
    text = request.json.get('text', '')
    if not text:
        return jsonify({'error': 'Please enter some text'})

    hashtags = generate_hashtags(text)
    return jsonify({'hashtags': hashtags})


if __name__ == '__main__':
    app.run(debug=True)
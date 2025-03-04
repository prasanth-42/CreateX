# app.py
from flask import Flask, render_template, request, jsonify
from gramformer import Gramformer
import torch

app = Flask(__name__)


def correct_grammar(text):
    gf = Gramformer(models=1, use_gpu=torch.cuda.is_available())
    corrected_sentences = gf.correct(text, max_candidates=1)
    corrected_words = []

    # Compare original and corrected text
    original_words = text.split()
    corrected_words_list = " ".join(corrected_sentences).split()

    for original, corrected in zip(original_words, corrected_words_list):
        if original != corrected:
            corrected_words.append((original, corrected))

    return " ".join(corrected_sentences), corrected_words


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check_grammar', methods=['POST'])
def check_grammar():
    text = request.json.get('text', '')
    if not text:
        return jsonify({'error': 'Please enter some text'})

    corrected_text, corrected_words = correct_grammar(text)
    return jsonify({
        'corrected_text': corrected_text,
        'corrected_words': corrected_words
    })


if __name__ == '__main__':
    app.run(debug=True)
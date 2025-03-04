from flask import Flask, render_template, request, jsonify
from transformers import pipeline

app = Flask(__name__)

# Load summarization pipeline
summarizer = pipeline("summarization")


def summarize_text(text):
    summary = summarizer(text, max_length=70, min_length=30, do_sample=False)
    return summary[0]['summary_text']


@app.route('/')
def home():
    return render_template('script_to_description.html')


@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        text = request.json['text']
        if not text:
            return jsonify({'error': 'Please enter some text to summarize.'}), 400

        summary = summarize_text(text)
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
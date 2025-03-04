from flask import Flask, render_template, request, jsonify
from googletrans import Translator

app = Flask(__name__)

# Mapping language names to ISO language codes
LANGUAGE_CODES = {
    "Afrikaans": "af", "Albanian": "sq", "Amharic": "am", "Arabic": "ar",
    "Bangla": "bn", "Chinese (Simplified)": "zh-cn", "Chinese (Traditional)": "zh-tw",
    "Dutch": "nl", "English": "en", "French": "fr", "German": "de",
    "Hindi": "hi", "Italian": "it", "Japanese": "ja", "Kannada": "kn",
    "Korean": "ko", "Malayalam": "ml", "Marathi": "mr", "Portuguese": "pt",
    "Russian": "ru", "Spanish": "es", "Tamil": "ta", "Telugu": "te", "Urdu": "ur",
}

@app.route('/')
def home():
    # Pass the list of language names to the template
    return render_template('translator.html', languages=LANGUAGE_CODES.keys())

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        text = data.get('text', '')
        target_lang_name = data.get('target_language', 'English')  # Default to English

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Convert language name to language code
        target_lang = LANGUAGE_CODES.get(target_lang_name)
        if not target_lang:
            return jsonify({'error': 'Invalid target language'}), 400

        translator = Translator()
        translation = translator.translate(text, dest=target_lang)

        return jsonify({
            'translation': translation.text,
            'source_language': translation.src
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
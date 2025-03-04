from flask import Flask, render_template, request, send_file, jsonify
from gtts import gTTS
import os
import time
from pathlib import Path

app = Flask(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = Path('static/audio')
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

@app.route('/')
def home():
    return render_template('text_to_speech.html')

@app.route('/transform', methods=['POST'])
def transform():
    try:
        text = request.form.get('text', '')
        if not text:
            return jsonify({'error': 'Please enter some text'}), 400

        # Generate unique filename
        filename = f"speech_{os.urandom(4).hex()}.mp3"
        filepath = UPLOAD_FOLDER / filename

        # Convert text to speech
        tts = gTTS(text=text, lang='en')
        tts.save(str(filepath))

        return jsonify({
            'success': True,
            'message': 'Audio generated successfully!',
            'filename': filename
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    try:
        file_path = UPLOAD_FOLDER / filename
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        return send_file(
            file_path,
            mimetype='audio/mp3',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/play/<filename>')
def play(filename):
    try:
        file_path = UPLOAD_FOLDER / filename
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        return send_file(
            file_path,
            mimetype='audio/mp3'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Clean up old audio files
@app.before_request
def cleanup_old_files():
    try:
        # Delete files older than 1 hour
        current_time = time.time()
        for file in UPLOAD_FOLDER.glob('*.mp3'):
            if current_time - file.stat().st_mtime > 3600:
                file.unlink()
    except Exception:
        pass

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import os
from werkzeug.utils import secure_filename
import audioread
import wave

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def convert_mp3_to_wav(mp3_path, wav_path):
    """ Convert MP3 to WAV using audioread and wave """
    try:
        with audioread.audio_open(mp3_path) as source:
            with wave.open(wav_path, 'wb') as wav_file:
                wav_file.setnchannels(source.channels)
                wav_file.setsampwidth(2)  # 16-bit audio
                wav_file.setframerate(source.samplerate)

                for buffer in source:
                    wav_file.writeframes(buffer)

        return wav_path
    except Exception as e:
        return None


def audio_file_to_text(audio_file_path):
    recognizer = sr.Recognizer()

    # Convert MP3 to WAV if needed
    if audio_file_path.endswith(".mp3"):
        wav_path = audio_file_path.replace(".mp3", ".wav")
        audio_file_path = convert_mp3_to_wav(audio_file_path, wav_path)

        if audio_file_path is None:
            return {"success": False, "error": "Failed to convert MP3 to WAV"}

    # Recognize text
    try:
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return {"success": True, "text": text}
    except sr.UnknownValueError:
        return {"success": False, "error": "Could not understand the audio. Try again!"}
    except sr.RequestError:
        return {"success": False, "error": "Could not request results. Check your internet connection."}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.route('/')
def index():
    return render_template('audio_to_text.html')


@app.route('/convert', methods=['POST'])
def convert():
    if 'audio' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"})

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"success": False, "error": "No file selected"})

    if audio_file and audio_file.filename.endswith(('.mp3', '.wav')):
        filename = secure_filename(audio_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(filepath)

        result = audio_file_to_text(filepath)

        # Clean up the file
        os.remove(filepath)

        return jsonify(result)

    return jsonify({"success": False, "error": "Invalid file format"})


if __name__ == '__main__':
    app.run(debug=True)
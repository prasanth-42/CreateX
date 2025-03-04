from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import moviepy.editor as mp
import speech_recognition as sr
from pathlib import Path
import threading
import time

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store transcription progress
transcription_status = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def transcribe_video(file_path, task_id):
    try:
        transcription_status[task_id] = {'progress': 0, 'status': 'Starting transcription...'}

        # Convert video to audio
        transcription_status[task_id] = {'progress': 10, 'status': 'Converting video to audio...'}
        video = mp.VideoFileClip(file_path)

        # Create temp directory for audio
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        audio_path = temp_dir / f"temp_audio_{task_id}.wav"

        # Extract audio
        audio = video.audio
        audio.write_audiofile(str(audio_path), logger=None)
        video.close()

        transcription_status[task_id] = {'progress': 50, 'status': 'Transcribing audio...'}

        # Initialize recognizer
        recognizer = sr.Recognizer()

        # Transcribe audio
        with sr.AudioFile(str(audio_path)) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        transcription_status[task_id] = {
            'progress': 100,
            'status': 'Complete',
            'text': text
        }

        # Cleanup
        try:
            audio_path.unlink()  # Delete audio file
            for file in temp_dir.iterdir():
                file.unlink()  # Remove any remaining files
            temp_dir.rmdir()  # Remove temp directory if empty
        except Exception as e:
            print(f"Cleanup error: {e}")

    except Exception as e:
        transcription_status[task_id] = {
            'progress': 0,
            'status': f'Error: {str(e)}',
            'error': True
        }

@app.route('/')
def index():
    return render_template('video_to_text.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Generate task ID
        task_id = str(int(time.time()))

        # Start transcription in background
        thread = threading.Thread(
            target=transcribe_video,
            args=(file_path, task_id)
        )
        thread.daemon = True
        thread.start()

        return jsonify({'task_id': task_id})

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/status/<task_id>')
def get_status(task_id):
    return jsonify(transcription_status.get(task_id, {'progress': 0, 'status': 'Task not found'}))

if __name__ == '__main__':
    app.run(debug=True)
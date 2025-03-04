from flask import Flask, render_template, request, send_file, jsonify
import os
import time
from moviepy.editor import VideoFileClip
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'temp_uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('video_to_audio.html')

@app.route('/vta', methods=['POST'])
def vta():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file uploaded'}), 400

    video_file = request.files['video']
    output_format = request.form.get('format', 'mp3').lower()

    if video_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Save uploaded video
        video_filename = secure_filename(video_file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        video_file.save(video_path)

        # Convert to audio
        video = VideoFileClip(video_path)
        audio_filename = f"audio_{os.path.splitext(video_filename)[0]}.{output_format}"
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)

        if output_format == "mp3":
            video.audio.write_audiofile(audio_path, codec="mp3")
        elif output_format == "wav":
            video.audio.write_audiofile(audio_path, codec="pcm_s16le", fps=44100)
        else:
            return jsonify({'error': 'Unsupported format'}), 400

        video.close()  # Ensure MoviePy releases the file handle
        os.remove(video_path)  # Cleanup video file

        return send_file(
            audio_path,
            as_attachment=True,
            download_name=audio_filename,
            mimetype=f'audio/{output_format}'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        time.sleep(1)
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except PermissionError:
                pass  # Ignore error if file is still in use

if __name__ == '__main__':
    app.run(debug=True)

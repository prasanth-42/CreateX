# app.py
from flask import Flask, render_template, request, send_file
from PIL import Image
import io
import base64

app = Flask(__name__)

PLATFORM_SIZES = {
    "YouTube Thumbnail": (1280, 720),
    "Instagram Post": (1080, 1080),
    "Instagram Story": (1080, 1920),
    "Facebook Post": (1200, 630),
    "Twitter Post": (1024, 512)
}


def resize_image(image, target_size):
    return image.resize(target_size, Image.LANCZOS)


@app.route('/')
def index():
    return render_template('imageresizer.html', platforms=PLATFORM_SIZES)


@app.route('/resize', methods=['POST'])
def resize():
    if 'image' not in request.files:
        return {'error': 'No image uploaded'}, 400

    file = request.files['image']
    platform = request.form.get('platform')

    if not file or not platform:
        return {'error': 'Missing required fields'}, 400

    try:
        # Open and resize image
        image = Image.open(file)
        resized = resize_image(image, PLATFORM_SIZES[platform])

        # Convert to base64 for preview
        buffered = io.BytesIO()
        resized.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # Save resized image for download
        download_buffer = io.BytesIO()
        resized.save(download_buffer, format="PNG")
        download_buffer.seek(0)

        return {
            'preview': f'data:image/png;base64,{img_str}',
            'success': True
        }

    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/download', methods=['POST'])
def download():
    try:
        # Get the base64 image data
        image_data = request.json.get('image').split(',')[1]
        platform = request.json.get('platform')

        # Convert base64 to bytes
        image_bytes = base64.b64decode(image_data)

        # Create BytesIO object
        buffer = io.BytesIO(image_bytes)
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'resized_{platform.replace(" ", "_")}.png'
        )

    except Exception as e:
        return {'error': str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True)
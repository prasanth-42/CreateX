from flask import Flask, render_template, request, jsonify, send_file
import requests
from monsterapi import client
from io import BytesIO

app = Flask(__name__)

# Initialize the MonsterAPI client
API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6IjlkYjVkOGZiZGRmMjk5MGRjZmY3M2E0NTRkYjY0ZGE2IiwiY3JlYXRlZF9hdCI6IjIwMjUtMDItMTRUMDQ6Mjg6MDEuMDQ0ODczIn0.nX96IiFuTAZRMnaSLjRtmj2T1UrPpHmwsnLZAr_sSkE"
monster_client = client(API_KEY)


@app.route('/')
def home():
    return render_template('Title_to_Thumbnail.html')


@app.route('/ttt', methods=['POST'])
def generate_image():
    try:
        user_prompt = request.form.get('prompt')

        if not user_prompt:
            return jsonify({'error': 'Please provide a prompt'}), 400

        # Define input parameters
        model = "txt2img"
        input_data = {
            "prompt": user_prompt,
            "negprompt": "deformed, bad anatomy, disfigured, poorly drawn face",
            "samples": 1,
            "steps": 50,
            "aspect_ratio": "square",
            "guidance_scale": 7.5,
            "seed": 2414,
        }

        # Generate the image
        result = monster_client.generate(model, input_data)

        if "output" in result:
            image_url = result["output"][0]
            # Fetch the image
            response = requests.get(image_url)
            if response.status_code == 200:
                return jsonify({
                    'success': True,
                    'image_url': image_url
                })

        return jsonify({'error': 'Failed to generate image'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/img', methods=['POST'])
def download_image():
    try:
        image_url = request.form.get('image_url')
        response = requests.get(image_url)

        if response.status_code == 200:
            return send_file(
                BytesIO(response.content),
                mimetype='image/png',
                as_attachment=True,
                download_name='generated_image.png'
            )

        return jsonify({'error': 'Failed to download image'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
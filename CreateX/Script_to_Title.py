from flask import Flask, render_template, request, jsonify
from transformers import T5Tokenizer, T5ForConditionalGeneration

app = Flask(__name__)


# Load Model and Tokenizer
def load_model():
    model_name = "google/flan-t5-base"
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    return model, tokenizer


model, tokenizer = load_model()


# Function to Generate Title
def generate_title(script):
    input_text = f"Generate a creative movie title for the following script: {script}"
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    output = model.generate(
        **inputs,
        max_length=30,  # Increased max_length for better generation
        num_beams=5,
        temperature=0.7,  # Adding randomness
        top_p=0.9,
        early_stopping=True
    )
    title = tokenizer.decode(output[0], skip_special_tokens=True)
    return title


@app.route('/')
def home():
    return render_template('script_to_title.html')


@app.route('/stf', methods=['POST'])
def stf():
    script = request.json.get('script')
    if not script:
        return jsonify({'error': 'Please enter a script'}), 400

    try:
        generated_title = generate_title(script)
        return jsonify({'title': generated_title})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

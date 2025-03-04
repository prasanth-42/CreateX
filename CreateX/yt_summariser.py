from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline

app = Flask(__name__)

# Load the Hugging Face summarization pipeline
summarizer = pipeline("summarization")


def get_transcript(video_id):
    try:
        # Retrieve the transcript for the given video ID
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([t['text'] for t in transcript])  # Join the transcript parts
        return transcript_text
    except Exception as e:
        return str(e)


def get_summary(text):
    # Split the text into chunks of 1000 characters to avoid model input size limits
    chunk_size = 1000
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    # Summarize each chunk and combine them
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=150, min_length=50, do_sample=False)
        summaries.append(summary[0]['summary_text'])

    # Join all summaries into a single summary
    return " ".join(summaries)


@app.route('/summarize', methods=['GET'])
def summarize_video():
    video_url = request.args.get('video_url')
    if not video_url:
        return jsonify({"error": "Missing video URL"}), 400

    # Extract the YouTube video ID from the URL
    video_id = video_url.split("v=")[-1]

    # Get the transcript and summarize it
    transcript_text = get_transcript(video_id)
    if "error" in transcript_text.lower():
        return jsonify({"error": "Unable to retrieve transcript"}), 400

    summary = get_summary(transcript_text)

    return jsonify({"summary": summary}), 200


if __name__ == '__main__':
    app.run(debug=True)

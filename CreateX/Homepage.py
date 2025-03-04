import subprocess
from flask import Flask, render_template_string, redirect, url_for, render_template
from Grammer_check import check_grammar
from Hashtag_generator import generate
from Image_Resizer import resize
from Script_Validation import validate
from Script_to_Title import stf
from Script_to_description import summarize
from Text_to_Speech import transform
from Title_To_Thumbnail import generate_image
from Video_To_Audio import vta
from audio_to_text import convert
from translation import translate
from video_to_text import upload_file
from video_to_text import get_status

app = Flask(__name__)

# HTML template matching the provided interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CreateX</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div class="flex h-screen">
        <!-- Sidebar -->
        <div class="w-64 bg-white shadow-lg">
            <div class="p-4">
                <h1 class="text-2xl font-bold text-yellow-600">CreateX</h1>
            </div>

            <nav class="mt-8">
                <div class="px-4 space-y-2">
                    <a href="{{ url_for('index') }}" class="flex items-center space-x-2 bg-purple-600 text-white w-full p-3 rounded-lg hover:bg-purple-700 transition-colors">
                        <span>Home</span>
                    </a>

                    <a href="/history" class="flex items-center space-x-2 text-gray-600 w-full p-3 rounded-lg hover:bg-gray-100 transition-colors">
                        <span>History</span>
                    </a>

                    <a href="/billing" class="flex items-center space-x-2 text-gray-600 w-full p-3 rounded-lg hover:bg-gray-100 transition-colors">
                        <span>Billing</span>
                    </a>

                    <a href="/setting" class="flex items-center space-x-2 text-gray-600 w-full p-3 rounded-lg hover:bg-gray-100 transition-colors">
                        <span>Setting</span>
                    </a>
                </div>
            </nav>

            <div class="absolute bottom-0 left-0 w-64 p-4 bg-purple-600 text-white">
                <div class="mb-2">Credits</div>
                <div class="text-sm">6408/10000 credits used</div>
                <button class="mt-2 w-full bg-white text-purple-600 rounded-lg py-2 hover:bg-gray-100 transition-colors">
                    Upgrade
                </button>
            </div>
        </div>

        <!-- Main Content -->
        <div class="flex-1 overflow-auto">
            <header class="bg-white p-4 shadow-sm">
                <div class="flex justify-between items-center">
                    <div class="relative w-64">
                        <input type="text" id="searchInput" placeholder="Search..."
                            class="pl-10 pr-4 py-2 w-full rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-600">
                    </div>
                    <button class="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors">
                        Join Membership just for $9.99/Month
                    </button>
                </div>
            </header>

            <main class="p-6">
                <div class="mb-8">
                    <h2 class="text-2xl font-bold text-center mb-2">Browse All Templates</h2>
                    <p class="text-center text-gray-600">What would you like to create today?</p>
                    <div class="max-w-2xl mx-auto mt-4">
                        <div class="relative">
                            <input type="text" placeholder="Search templates..."
                                class="pl-10 pr-4 py-3 w-full rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-600">
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <!-- Content Generation Tools -->
                    <a href="{{ url_for('audio_to_text') }}" class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer">
                        <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600 mb-4">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-semibold mb-2">Audio To Text</h3>
                        <p class="text-gray-600">Convert audio files to text format</p>
                    </a>

                    <a href="{{ url_for('video_to_text') }}" class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer">
                        <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600 mb-4">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-semibold mb-2">Video To Text</h3>
                        <p class="text-gray-600">Extract text from video content</p>
                    </a>

                    <a href="{{ url_for('grammar_check') }}" class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer">
                        <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600 mb-4">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-semibold mb-2">Grammar Check</h3>
                        <p class="text-gray-600">Check and improve text grammar</p>
                    </a>

                    <a href="{{ url_for('script_hashtags') }}" class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer">
                        <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600 mb-4">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-semibold mb-2">Script Hashtags</h3>
                        <p class="text-gray-600">Generate relevant hashtags</p>
                    </a>

                    <a href="{{ url_for('script_to_title') }}" class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer">
                        <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600 mb-4">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-semibold mb-2">Script To Title</h3>
                        <p class="text-gray-600">Convert scripts to engaging titles</p>
                    </a>
                    <a href="{{ url_for('image_resizer') }}" class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer">
                       <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 mb-4">
                           <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path>
                           </svg>
                       </div>
                       <h3 class="text-lg font-semibold mb-2">Image Resizer</h3>
                       <p class="text-gray-600">Resize images quickly and efficiently</p>
                    </a>
                    <a href="{{ url_for('script_to_descript') }}" class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer">
                        <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center text-green-600 mb-4">
                            <!-- New icon for "Script to Description" -->
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16h8M8 12h8M4 4h16v16H4z"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-semibold mb-2">Script to Description</h3>
                        <p class="text-gray-600">Summarize your script into an engaging description</p>
                    </a>
                    <a href="{{ url_for('script_validation') }}" class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer">
                        <div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center text-yellow-600 mb-4">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-semibold mb-2">Script Validation</h3>
                        <p class="text-gray-600">Check and refine your script for better impact</p>
                    </a>
                    <a href="{{ url_for('translate') }}" class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer">
                        <div class="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600 mb-4">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v12m12-3h-8m8 0l-4 4m4-4l-4-4"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-semibold mb-2">Translator</h3>
                        <p class="text-gray-600">Translate text between multiple languages</p>
                    </a>
                    <a href="{{ url_for('thumbnail') }}" class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer">
                        <div class="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center text-red-600 mb-4">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4h16v16H4z"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-semibold mb-2">Title to Thumbnail</h3>
                        <p class="text-gray-600">Generate a thumbnail from your video title</p>
                    </a>
                    <a href="{{ url_for('text_to_speech') }}" class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer">
                        <div class="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center text-teal-600 mb-4">
                            <!-- New icon for "Text to Speech" -->
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 14l7-7 7 7M5 10h14M12 14v4m0-8V3"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-semibold mb-2">Text to Speech</h3>
                        <p class="text-gray-600">Convert text into natural-sounding speech</p>
                    </a>
                    <a href="{{ url_for('video_to_audio') }}" class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer">
                        <div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center text-orange-600 mb-4">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a4 4 0 00-8 0v2m8 0v2a4 4 0 01-8 0V9m8 0h2a2 2 0 002-2V5a2 2 0 00-2-2h-2m-8 6H5a2 2 0 01-2-2V5a2 2 0 012-2h2"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-semibold mb-2">Video to Audio</h3>
                        <p class="text-gray-600">Extract audio from video files</p>
                    </a>
                    
                    <a href="/youtube-summarizer" class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer">
                        <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600 mb-4">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-semibold mb-2">YouTube Summarizer</h3>
                        <p class="text-gray-600">Generate video summaries</p>
                    </a>
                </div>
            </main>
        </div>
    </div>

    <script>
        // Search functionality
        document.querySelectorAll('input[type="text"]').forEach(input => {
            input.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase();
                const cards = document.querySelectorAll('.grid > a');
                cards.forEach(card => {
                    const title = card.querySelector('h3').textContent.toLowerCase();
                    const description = card.querySelector('p').textContent.toLowerCase();
                    card.style.display = title.includes(query) || description.includes(query) ? 'block' : 'none';
                });
            });
        });
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


# Routes for each tool
@app.route('/audio_to_text')
def audio_to_text():
    return render_template('audio_to_text.html')

@app.route('/script_to_descript')
def script_to_descript():
    return render_template('script_to_description.html')

@app.route('/video_to_text')
def video_to_text():
    return render_template('video_to_text.html')

@app.route('/text_to_speech')
def text_to_speech():
    return render_template('text_to_speech.html')


@app.route('/grammar-check')
def grammar_check():
    return render_template('index.html')


@app.route('/script_hashtags')
def script_hashtags():
    return render_template('hashtag.html')


@app.route('/script_to_title')
def script_to_title():
    return render_template('script_to_title.html')

@app.route('/script_validation')
def script_validation():
    return render_template('script_validation.html')

@app.route('/image_resizer')
def image_resizer():
    return render_template('imageresizer.html')

@app.route('/translate')
def translate():
    return render_template('translator.html')

@app.route('/thumbnail')
def thumbnail():
    return render_template('Title_To_Thumbnail.html')

@app.route('/video_to_audio')
def video_to_audio():
    return render_template('video_to_audio.html')

@app.route('/youtube-summarizer')
def youtube_summarizer():
    return redirect('/youtube_summarizer.py')

@app.route('/check_grammar', methods=['POST'])
def check_grammar_route():
    return check_grammar()

@app.route('/generate', methods=['POST'])
def generate_route():
    return generate()

@app.route('/convert', methods=['POST'])
def convert_route():
    return convert()

@app.route('/stf', methods=['POST'])
def stf_route():
    return stf()

@app.route('/resize', methods=['POST'])
def resize_route():
    return resize()

@app.route('/summarize', methods=['POST'])
def summarize_route():
    return summarize()

@app.route('/ttt', methods=['POST'])
def ttt_route():
    return generate_image()

@app.route('/validate', methods=['POST'])
def validate_route():
    return validate()

@app.route('/translate', methods=['POST'])
def translate_route():
    return translate()

@app.route('/vta', methods=['POST'])
def vta_route():
    return vta()

# @app.route('/upload', methods=['POST'])
# def upload_route():
#     return upload_file()

@app.route('/status/<task_id>')
def get_status_route(task_id):
    return get_status(task_id)

@app.route('/transform', methods=['POST'])
def transform_route():
    return transform()


@app.route('/upload', methods=['POST'])
def upload_route():
    return upload_file()


if __name__ == '__main__':
    app.run(debug=True)
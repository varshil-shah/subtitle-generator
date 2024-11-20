import assemblyai as aai
import requests
from flask import Flask, request, jsonify, send_file
import os
from tempfile import NamedTemporaryFile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variables
aai.settings.api_key = os.getenv('API_KEY')

app = Flask(__name__)

# Create a directory for temporary files
TEMP_DIR = 'temp'
os.makedirs(TEMP_DIR, exist_ok=True)

# Add timeout configuration for requests
DOWNLOAD_TIMEOUT = 300  # 5 minutes
TRANSCRIPTION_TIMEOUT = 600  # 10 minutes


def download_video(url):
    # Download video from the URL with increased timeout
    response = requests.get(url, timeout=DOWNLOAD_TIMEOUT, stream=True)
    temp_file = NamedTemporaryFile(delete=False, suffix='.mp4', dir=TEMP_DIR)
    with open(temp_file.name, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return temp_file.name


@app.route('/generate-subtitle', methods=['POST'])
def generate_subtitles():
    try:
        # Get the video URL from the request
        video_url = request.json.get('video_url')
        if not video_url:
            return jsonify({"error": "No video URL provided"}), 400

        # Download the video
        video_path = download_video(video_url)

        try:
            # Transcribe the video using AssemblyAI
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(
                video_path,
                config=aai.TranscriptionConfig(
                    # Remove max_delay and use standard configuration
                )
            )

            # Export subtitles as SRT
            subtitles = transcript.export_subtitles_srt()

            # Save the subtitles to a temporary file
            subtitle_path = os.path.join(TEMP_DIR, "subtitles.srt")
            with open(subtitle_path, "w") as f:
                f.write(subtitles)

            # Return the subtitle file as response
            return send_file(subtitle_path, as_attachment=True)

        finally:
            # Clean up temporary files
            if os.path.exists(video_path):
                os.remove(video_path)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Service is running"
    }), 200

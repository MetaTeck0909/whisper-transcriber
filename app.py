from flask import Flask, request, jsonify
from google.cloud import storage
import whisper
import os
import requests

# Config
BUCKET_NAME = "resumes-audio-ai-automeeting-50625"
WEBHOOK_MAKE_URL = "https://hook.eu2.make.com/366zwi7iy1qik15ruatqalqdvwvovadw"

# Authentification GCP
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

# App Flask
app = Flask(__name__)
model = whisper.load_model("base")

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    data = request.get_json()
    filename = data.get("filename")

    if not filename:
        return jsonify({"error": "filename is required"}), 400

    try:
        # Téléchargement depuis GCS
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        local_path = "/tmp/" + os.path.basename(filename)
        blob.download_to_filename(local_path)

        # Transcription
        result = model.transcribe(local_path)
        transcript = result["text"]

        # Envoi vers Make
        requests.post(WEBHOOK_MAKE_URL, json={"text": transcript})

        return jsonify({"status": "ok", "transcript": transcript[:200] + "..."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

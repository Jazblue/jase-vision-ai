from flask import Flask, request, jsonify, render_template
import requests
import base64
import binascii

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "hf.co/openbmb/MiniCPM-V-4.7-1B-gguf:Q4_K_M"
MAX_IMAGE_SIZE = 8 * 1024 * 1024

def valid_image(image_bytes):
    if image_bytes.startswith(b"\xff\xd8\xff"):
        return True
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    if len(image_bytes) >= 12 and image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return True
    return False

def analyse_image(image_bytes):
    if not image_bytes or len(image_bytes) > MAX_IMAGE_SIZE:
        return jsonify({"error": "Image must be between 1 byte and 8 MB."}), 400
    if not valid_image(image_bytes):
        return jsonify({"error": "Please upload a valid JPG, PNG or WEBP image."}), 400
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": "Briefly describe the visible scene in two sentences. Be accurate and concise.",
                "images": [image_base64],
                "stream": False
            },
            timeout=180
        )
        response.raise_for_status()
        return jsonify({"description": response.json()["response"]})
    except requests.exceptions.Timeout:
        return jsonify({"error": "AI analysis timed out. Please try again."}), 504
    except requests.exceptions.RequestException:
        app.logger.exception("Ollama connection failed")
        return jsonify({"error": "Could not connect to the AI service."}), 502
    except (ValueError, KeyError):
        return jsonify({"error": "The AI returned an unexpected response."}), 502

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyse", methods=["POST"])
def analyse():
    data = request.get_json(silent=True)
    if not data or not isinstance(data.get("image"), str):
        return jsonify({"error": "No valid webcam image received."}), 400
    try:
        image_data = data["image"].split(",")[-1]
        image_bytes = base64.b64decode(image_data, validate=True)
    except (ValueError, binascii.Error):
        return jsonify({"error": "Invalid image data."}), 400
    return analyse_image(image_bytes)

@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"error": "Please select an image."}), 400
    image = request.files["image"]
    image_bytes = image.read(MAX_IMAGE_SIZE + 1)
    return analyse_image(image_bytes)

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({"error": "Upload is too large. Maximum request size is 10 MB."}), 413

if __name__ == "__main__":
    # Keep Flask local; publish it only through a separately protected tunnel.
    app.run(host="127.0.0.1", port=5000, debug=False)

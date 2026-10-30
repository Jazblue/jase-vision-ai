# Jase Vision AI

A locally hosted AI vision assistant that lets an invited visitor ask a vision-language model to describe an image from their webcam or an uploaded file.

The application uses **Flask**, **Ollama** and **MiniCPM-V**. The model runs on the host computer rather than relying on a hosted vision API. A Cloudflare Tunnel and Cloudflare Access can provide a controlled HTTPS entry point for invited testers.

> **Demo access:** The live instance is invite-only. A public source repository does not make the running computer or its AI endpoint public.

## Features

- **Webcam capture:** the visitor explicitly grants browser camera permission; the browser captures a frame and sends it for analysis.
- **Image uploads:** JPG, PNG and WEBP uploads, limited to 8 MB per image.
- **Local inference:** image analysis is sent to the configured Ollama model on the host machine.
- **No application-side image archive:** the Flask routes process image bytes in memory and do not save uploaded images to disk.
- **Bounded requests and errors:** request-size limits, basic file-signature checks, timeouts and useful API error responses.
- **Access-controlled remote testing:** designed to sit behind an HTTPS tunnel protected by an identity-aware access layer.

## Architecture

~~~text
Visitor browser
  ├── Explicit webcam permission → capture a frame
  └── Select an image file
              |
              | HTTPS
              v
Cloudflare Access (invite-only policy)
              |
              v
Cloudflare Tunnel
              |
              v
Flask application (loopback interface)
              |
              v
Ollama local API
              |
              v
MiniCPM-V vision-language model
              |
              v
Description returned to that browser request
~~~

The tunnel is an optional deployment layer. The Flask app itself binds to the loopback interface; do not expose the Ollama API port directly to the internet.

## Technology

| Component | Role |
|---|---|
| Python | Application runtime |
| Flask | Web application and JSON/upload endpoints |
| Ollama | Local model runtime and inference API |
| MiniCPM-V | Vision-language model |
| HTML, CSS and JavaScript | Webcam capture, image preview and upload UI |
| Cloudflare Tunnel | Optional HTTPS connectivity to the local application |
| Cloudflare Access | Invite-only authentication in the hosted demo |

## Project structure

~~~text
jase-vision-ai/
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
├── SECURITY.md
└── templates/
    └── index.html
~~~

## Run locally

### 1. Install prerequisites

- Python 3.10 or later
- [Ollama](https://ollama.com/)
- A compatible MiniCPM-V model available in Ollama

### 2. Download / start the model

The default model identifier in app.py is:

~~~text
hf.co/openbmb/MiniCPM-V-4.7-1B-gguf:Q4_K_M
~~~

Run it once with Ollama so the model is available locally:

~~~bash
ollama run hf.co/openbmb/MiniCPM-V-4.7-1B-gguf:Q4_K_M
~~~

If you use a different Ollama model tag, update the MODEL value in app.py.

### 3. Install Python dependencies

Create and activate a virtual environment:

**Windows PowerShell**
~~~powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
~~~

**macOS / Linux**
~~~bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
~~~

### 4. Start the application

~~~bash
python app.py
~~~

Open http://127.0.0.1:5000.

The browser offers two independent ways to provide an image:
1. Select **Start webcam**, approve camera access, then choose **Analyse webcam**.
2. Select a JPG, PNG or WEBP file, check the preview, then choose **Analyse uploaded image**.

Camera access is requested by the visitor's own browser. The application does not activate the host computer's webcam for remote visitors.

## API endpoints

### POST /analyse

Accepts JSON containing a data URL in the image field. Used by the webcam interface.

### POST /upload

Accepts multipart/form-data with an image file field. Supports JPEG, PNG and WEBP image signatures.

Both routes return JSON containing either a description or an error message.

## Remote / invite-only deployment

The hosted demonstration uses a local Flask service behind a Cloudflare Tunnel and Cloudflare Access.

For a similar deployment:

1. Keep Flask bound to 127.0.0.1.
2. Run the tunnel connector on the same host and route only the chosen HTTPS hostname to the local Flask port.
3. Put a Cloudflare Access self-hosted application in front of that hostname.
4. Use an explicit allow-list policy for invited email addresses.
5. Keep tunnel credentials and configuration files outside this repository.
6. Do not publish Ollama's API port or expose the local machine directly.

**Important:** this repository intentionally does not include tunnel IDs, tunnel credentials, Access policy identifiers, private host configuration or any network address for the machine running the model.

## Privacy and limitations

- The browser sends the selected image or captured frame to the Flask application for inference.
- The Flask application does not write image uploads to a permanent application storage directory.
- The image is forwarded to the local Ollama API for analysis.
- This does not guarantee that every other component in a deployment (browser, operating system, tunnel provider, logs or model runtime) retains no metadata. Review those components and their policies separately.
- The current implementation is a controlled demonstration, not a hardened multi-tenant production service.
- It does not yet include per-user quotas, a job queue, rate limiting, malware scanning, advanced image decoding, or a concurrency scheduler. A single local model and PC have finite capacity.
- Only invite trusted testers until those controls are added.

## Security

Read SECURITY.md before exposing an instance beyond localhost. Never commit secrets, tunnel credentials, private keys, .env files or personal network details.

## Project website

The GitHub Pages project overview is published from the docs/ folder when Pages is enabled for the main branch.

## Acknowledgements

Built as a practical experiment in local vision AI, browser camera APIs, Python web applications and self-hosted inference.

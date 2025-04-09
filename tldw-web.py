from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import time
import dotenv
from typing import Optional, Dict, Any
import os
from tldw import summarize_video
import traceback

app = Flask(__name__)
app.config['PROXY_URL'] = None  # Default value

cors = CORS(app)  # Enable CORS for all routes

# More specific CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://tldw.tube",
            "http://localhost:5173", # for local development
        ],
        "methods": ["GET", "POST", "OPTIONS"],
    }
})

# Load environment variables
dotenv.load_dotenv()

# Rate limiting decorator
def rate_limit(limit=5):  # 60 requests per minute by default
    def decorator(f):
        requests = {}

        @wraps(f)
        def wrapped(*args, **kwargs):
            now = time.time()
            ip = request.remote_addr

            # Clean old entries
            requests[ip] = [t for t in requests.get(ip, []) if now - t < 60]

            if len(requests.get(ip, [])) >= limit:
                return jsonify({
                    "error": "Rate limit exceeded. Please try again later."
                }), 429

            requests.setdefault(ip, []).append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/article/summarize', methods=['POST'])
@rate_limit()
def summarize_article():
    try:
        data = request.get_json()

        if not data or 'url' not in data:
            return jsonify({
                "error": "Missing URL in request body"
            }), 400

        url = data['url']

        return jsonify(summarize_article(url)), 200
    except Exception as e:
        app.logger.error(f"Error processing video: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/summarize', methods=['POST'])
@rate_limit()
def summarize_video_api():
    try:
        data = request.get_json()

        if not data or 'url' not in data:
            return jsonify({
                "error": "Missing URL in request body"
            }), 400

        url = data['url']

        return jsonify(summarize_video(url)), 200
    except Exception as e:
        app.logger.error(f"Error processing video: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    from waitress import serve
    import argparse
    parser = argparse.ArgumentParser(description='Server configuration')
    parser.add_argument('--port', type=int, default=5000, help='Port number (default: 5000)')
    parser.add_argument('--proxy', default=os.getenv('PROXY_URL'), help='Proxy URL (default: PROXY_URL environment variable or None)')
    args = parser.parse_args()
    app.config['PROXY_URL'] = args.proxy
    print(f'Serving on port {args.port}')
    serve(app, host="0.0.0.0", port=args.port)

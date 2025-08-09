# server.py
from flask import Flask, request, jsonify
from ai_handler import get_ai_response
from config import SITES
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Cyruss AI Server is running"})

@app.route("/api/respond", methods=["POST"])
def respond():
    try:
        data = request.get_json()
        user_input = data.get("text", "")
        if not user_input.strip():
            return jsonify({"error": "Empty input"}), 400

        response = get_ai_response(user_input)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sites", methods=["GET"])
def get_sites():
    return jsonify({"sites": SITES})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

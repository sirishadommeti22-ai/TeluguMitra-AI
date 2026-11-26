import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
MODEL = "gemini-3.8-flash"

SYSTEM_PROMPT = """
You are ManaMitra-AI, a friendly college friend.

Explain English study material in natural Telugu + English mix.
Use simple everyday Telugu written in Telugu script where natural,
and familiar English technical terms when helpful.
Explain concepts step by step, with relatable examples.
Be warm, patient and encouraging, like a helpful classmate.
Do not merely translate word by word.
If the student asks a follow-up, answer it in the same style.
Keep the explanation clear and easy to understand.
If the student asks for something unrelated to study, still
respond politely and briefly in the same friendly style.
"""

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"reply": "Friend, first message type cheyyi 😊"}), 400

    if len(message) > 8000:
        return jsonify({"reply": "Friend, text konchem short chesi send cheyyi."}), 400

    if not API_KEY:
        return jsonify({
            "reply": "Friend, AI API key setup cheyyali. "
                     "Project folder lo .env file check cheyyi."
        }), 500

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Keep only recent, valid conversation messages.
    if isinstance(history, list):
        for item in history[-10:]:
            if not isinstance(item, dict):
                continue
            role = item.get("role")
            content = item.get("content")
            if role in ("user", "assistant") and isinstance(content, str):
                messages.append({
                    "role": role,
                    "content": content[:4000]
                })

    messages.append({"role": "user", "content": message})

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 800
            },
            timeout=60
        )

        if response.status_code != 200:
            print("AI API error:", response.status_code, response.text[:500])
            return jsonify({
                "reply": "Friend, AI response ippudu raledu. "
                         "API key, API access, credits check cheyyi."
            }), 502

        result = response.json()
        reply = result["choices"][0]["message"]["content"]

        return jsonify({"reply": reply})

    except requests.RequestException:
        return jsonify({
            "reply": "Friend, server connect avvaledu. Internet connection check cheyyi."
        }), 502


if __name__ == "__main__":
    app.run(debug=True)
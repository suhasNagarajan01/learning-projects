import json
import os
import re
import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

USERS_FILE = "users.json"

# Active session user tracking
current_user = {"key": None, "display_name": None, "preferences": []}
conversation = []

OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2"


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def normalize_name(name_str):
    if not name_str:
        return ""
    # Strip spaces and non-alphanumeric characters, convert to lowercase
    return re.sub(r"[^a-z0-9]", "", name_str.lower())


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/identify-user", methods=["POST"])
def identify_user():
    global current_user
    data = request.get_json() or {}
    raw_name = data.get("name", "").strip()
    middle_name = data.get("middle_name", "").strip()
    asked_middle = data.get("asked_middle", False)

    if not raw_name:
        return jsonify({"error": "Name is required"}), 400

    users = load_users()

    # Approach 2: Combine full name, remove spaces, and convert to lower continuous string
    combined_name = f"{raw_name} {middle_name}".strip() if middle_name else raw_name
    normalized_key = normalize_name(combined_name)

    # 1. Search existing users
    if normalized_key in users:
        current_user["key"] = normalized_key
        current_user["display_name"] = users[normalized_key].get(
            "display_name", raw_name
        )
        current_user["preferences"] = users[normalized_key].get(
            "preferences", []
        )
        return jsonify({
            "found": True,
            "display_name": current_user["display_name"],
            "preferences": current_user["preferences"],
        })

    # 2. If not found and middle name hasn't been asked yet, prompt user
    if not middle_name and not asked_middle:
        return jsonify({"found": False, "ask_middle_name": True})

    # 3. New User Registration
    new_user_key = normalize_name(combined_name)
    users[new_user_key] = {
        "display_name": combined_name,
        "preferences": [],
        "message_count": 0,
    }
    save_users(users)

    current_user["key"] = new_user_key
    current_user["display_name"] = combined_name
    current_user["preferences"] = []

    return jsonify({
        "found": False,
        "new_user": True,
        "display_name": combined_name,
        "preferences": [],
    })


def analyze_preferences_from_history():
    """Background preference extraction from the conversation history."""
    if not current_user["key"]:
        return

    user_prompts = [
        msg["content"] for msg in conversation if msg.get("role") == "user"
    ]

    analysis_messages = [
        {
            "role": "system",
            "content": (
                "You are an AI user profiling assistant. Analyze the user's messages and extract 3 to 5 short keyword preferences or interests "
                "(e.g. 'python', 'concise answers', 'flask', 'chess'). Output ONLY a comma-separated list of lower-case keywords."
            ),
        },
        {"role": "user", "content": "\n".join(user_prompts)},
    ]

    try:
        res = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MODEL_NAME,
                "messages": analysis_messages,
                "stream": False,
            },
            timeout=30,
        )
        if res.status_code == 200:
            raw_keywords = (
                res.json().get("message", {}).get("content", "").strip()
            )
            # Corrected list comprehension
            extracted = [
                kw.strip().lower()
                for kw in raw_keywords.split(",")
                if kw.strip() and len(kw.strip()) < 30
            ]

            users = load_users()
            user_data = users.get(current_user["key"], {})
            existing_prefs = set(user_data.get("preferences", []))
            existing_prefs.update(extracted)

            updated_prefs = list(existing_prefs)
            user_data["preferences"] = updated_prefs
            users[current_user["key"]] = user_data
            save_users(users)

            current_user["preferences"] = updated_prefs
    except Exception as e:
        print(f"Error extracting preferences: {e}")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_prompt = data.get("user_prompt", "").strip()

    if not user_prompt:
        return jsonify({"error": "Empty prompt"}), 400

    # Append user prompt to history
    conversation.append({"role": "user", "content": user_prompt})

    # Prepare message payload with personalized system agent prompt
    messages_payload = []
    if current_user["preferences"]:
        prefs_str = ", ".join(current_user["preferences"])
        system_prompt = {
            "role": "system",
            "content": f"You are a personalized AI assistant for {current_user['display_name'] or 'the user'}. Personalize your style and responses based on their preferences: {prefs_str}.",
        }
        messages_payload.append(system_prompt)

    messages_payload.extend(conversation)

    payload = {
        "model": MODEL_NAME,
        "messages": messages_payload,
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        response_data = response.json()

        bot_reply = response_data["message"]["content"].strip()
        conversation.append({"role": "assistant", "content": bot_reply})

        # Analyze user preferences upon reaching 10 messages
        user_msg_count = sum(
            1 for m in conversation if m.get("role") == "user"
        )
        if user_msg_count == 10:
            analyze_preferences_from_history()

        return jsonify({
            "reply": bot_reply,
            "preferences": current_user["preferences"],
        })

    except requests.exceptions.ConnectionError:
        conversation.pop()
        error_msg = "Error: Could not connect to Ollama. Make sure 'run_ollama.bat' is running from your pendrive."
        return jsonify({"reply": error_msg, "error": True}), 500
    except Exception as e:
        conversation.pop()
        return jsonify({"reply": f"An error occurred: {str(e)}", "error": True}), 500


@app.route("/clear", methods=["POST"])
def clear_chat():
    global conversation
    conversation = []
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run(debug=True)
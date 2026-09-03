import os
from flask import Flask, render_template, request, jsonify
from gemini_bot import GeminiBot
from dotenv import load_dotenv  # Import load_dotenv
app = Flask(__name__)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
# Instantiate GeminiBot instance
bot = GeminiBot("API_KEY")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json() or {}
    user_query = data.get("query", "").strip()

    if not user_query:
        return jsonify({"error": "Query field cannot be empty."}), 400

    # Call GeminiBot search handler
    result = bot.generate_search_response(user_query)

    if "error" in result:
        return jsonify({"error": result["error"]}), 500

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
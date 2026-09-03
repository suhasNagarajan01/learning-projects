import os
from flask import Flask, jsonify, render_template, request
from gemini_bot import StudyBuddyBot

app = Flask(__name__)
bot = StudyBuddyBot("API_KEY")

# In-memory storage for active quiz state (can be expanded to session-based)
current_quiz_data = {}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate-quiz", methods=["POST"])
def generate_quiz():
    global current_quiz_data
    data = request.get_json() or {}
    topic = data.get("topic", "").strip()

    if not topic:
        return jsonify({"error": "Topic is required."}), 400

    result = bot.generate_study_material(topic)

    if "error" in result:
        return jsonify({"error": result["error"]}), 500

    # Cache active quiz structure for grading step
    current_quiz_data = result.get("quiz", [])

    return jsonify(
        {"overview": result.get("overview", ""), "quiz": current_quiz_data}
    )


@app.route("/grade-quiz", methods=["POST"])
def grade_quiz():
    global current_quiz_data
    data = request.get_json() or {}
    user_answers = data.get("answers", {})

    if not current_quiz_data:
        return jsonify(
            {"error": "No active quiz found. Please start over."}
        ), 400

    score = 0
    total = len(current_quiz_data)
    results = []

    for q in current_quiz_data:
        q_id = str(q["id"])
        submitted_ans = user_answers.get(q_id, "No answer selected")
        correct_ans = q["correct_answer"]
        is_correct = submitted_ans == correct_ans

        if is_correct:
            score += 1

        results.append({
            "id": q["id"],
            "question": q["question"],
            "submitted_answer": submitted_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "explanation": q["explanation"],
        })

    return jsonify({"score": score, "total": total, "details": results})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
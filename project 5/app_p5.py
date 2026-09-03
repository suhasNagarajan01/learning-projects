import json
import os
import streamlit as st

st.title("Quiz Master BOT")
st.header("ENTER YOUR NAME AND GET STARTED WITH THE QUIZ")

# Input for user name
name = st.text_input("Enter your name:", key="username")
name = name.strip()

# Initialize session state variables if they don't exist
if "quiz_started" not in st.session_state:
  st.session_state.quiz_started = False
if "score" not in st.session_state:
  st.session_state.score = 0

# Define the 10 math questions
questions = [
    {
        "q": "What is 15 + 7?",
        "options": ["20", "22", "25", "24"],
        "answer": "22",
    },
    {
        "q": "What is 9 multiplied by 8?",
        "options": ["72", "81", "64", "56"],
        "answer": "72",
    },
    {
        "q": "What is 50 minus 17?",
        "options": ["33", "37", "43", "23"],
        "answer": "33",
    },
    {
        "q": "What is 81 divided by 9?",
        "options": ["7", "8", "9", "6"],
        "answer": "9",
    },
    {
        "q": "What is 25\% \of 200?",
        "options": ["25", "50", "75", "100"],
        "answer": "50",
    },
    {
        "q": "Solve for x: x + 5 = 12",
        "options": ["5", "6", "7", "8"],
        "answer": "7",
    },
    {
        "q": "What is the square root of 144?",
        "options": ["10", "11", "12", "14"],
        "answer": "12",
    },
    {
        "q": "What is 3 cubed (3³)?",
        "options": ["9", "18", "27", "30"],
        "answer": "27",
    },
    {
        "q": "What is 45 + 55 - 20?",
        "options": ["70", "80", "90", "100"],
        "answer": "80",
    },
    {
        "q": "If a triangle has angles 60° and 70°, what is the third angle?",
        "options": ["40°", "50°", "60°", "70°"],
        "answer": "50°",
    },
]

# Check and initialize leaderboard file if it doesn't exist
leaderboard_file = "leaderboard.json"
if not os.path.exists(leaderboard_file):
  with open(leaderboard_file, "w") as file:
    json.dump({}, file)

# Start button logic
if name and not st.session_state.quiz_started:
  if st.button("Start Quiz", type="primary"):
    st.session_state.quiz_started = True
    st.rerun()

elif not name:
  st.warning("Please enter your name above to start the quiz!")

# Display the quiz once started
if st.session_state.quiz_started and name:
  st.subheader(
      f"Welcome {name}! Answer carefully to top the leaderboard."
  )
  st.divider()

  # Using a form to wrap all questions and a single submit button
  with st.form("quiz_form"):
    user_answers = {}

    # Loop through questions and create radio buttons
    for i, q_data in enumerate(questions):
      st.markdown(f"**Q{i+1}: {q_data['q']}**")
      user_answers[i] = st.radio(
          f"Select answer for Q{i+1}",
          q_data["options"],
          key=f"q_{i}",
          label_visibility="collapsed",
      )
      st.write("")  # spacing

    # Submit button for the form
    submit_quiz = st.form_submit_button(
        "Submit Quiz & Check Score", type="primary"
    )

    if submit_quiz:
      # Calculate score in a pythonic way
      score = 0
      for i, q_data in enumerate(questions):
        if user_answers[i] == q_data["answer"]:
          score += 1

      st.session_state.score = score

      # Load leaderboard, update score, and save back
      with open(leaderboard_file, "r") as file:
        data = json.load(file)

      # Update score only if it's higher than previous score (optional logic)
      if name not in data or score > data[name]:
        data[name] = score

      with open(leaderboard_file, "w") as file:
        json.dump(data, file, indent=4)

      # Show results
      st.success(
          f"🎉 Quiz Submitted! Your Score: **{score} / {len(questions)}**"
      )

      # Display Leaderboard
      st.subheader("🏆 Leaderboard")
      sorted_leaderboard = sorted(
          data.items(), key=lambda x: x[1], reverse=True
      )
      for rank, (player, pts) in enumerate(sorted_leaderboard, 1):
        st.write(f"{rank}. **{player}** - {pts} points")
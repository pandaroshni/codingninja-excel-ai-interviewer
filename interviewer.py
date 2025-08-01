import streamlit as st
import os
import requests
from dotenv import load_dotenv
import datetime
import random

# Load API key from environment
groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))

# Master list of 10 Excel questions
all_questions = [
    "What is the difference between a workbook and a worksheet in Excel?",
    "How do you freeze panes in Excel?",
    "What is the use of the CONCATENATE function?",
    "What does the IF function do in Excel?",
    "How do you apply a filter to data in Excel?",
    "What is conditional formatting and how do you use it?",
    "How do you create a chart in Excel?",
    "Explain the difference between COUNT, COUNTA, and COUNTIF.",
    "How do you use the SUM function?",
    "What is the shortcut to insert the current date in a cell?"
]

# Initialize session state
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
    st.session_state.answers = []
    st.session_state.feedback = []
    st.session_state.interview_started = False
    st.session_state.selected_questions = random.sample(all_questions, 5)

# Welcome screen
if not st.session_state.interview_started:
    st.title("Excel Mock Interviewer")
    st.info("Welcome !! You'll be asked 5 randomly selected Excel questions. After each response, you'll receive instant feedback based on relevance, accuracy, and completeness. A summary will be provided at the end.")


    if st.button("Start Interview"):
        st.session_state.interview_started = True
        st.rerun()
else:
    st.title("Excel Mock Interviewer")

    if st.session_state.question_index < len(st.session_state.selected_questions):
        q = st.session_state.selected_questions[st.session_state.question_index]
        st.subheader(f"Q{st.session_state.question_index + 1}: {q}")
        user_input = st.text_area(
            "Your Answer:",
            key=f"user_answer_{st.session_state.question_index}"
        )

        if st.button("Submit Answer"):
            if user_input.strip() != "":
                with st.spinner("Evaluating your answer..."):
                    prompt = f"""
You are an expert Excel interviewer.
Question: {q}
Candidate's Answer: {user_input}

Evaluate the candidate's answer:
1. Score from 0 to 5.
2. Give clear feedback.
3. Provide improvement tips.

Respond exactly in this format:
Score: X/5
Feedback: ...
Improvement Tips: ...
                    """

                    headers = {
                        "Authorization": f"Bearer {groq_api_key}",
                        "Content-Type": "application/json"
                    }

                    payload = {
                        "model": "llama3-8b-8192",
                        "messages": [{"role": "user", "content": prompt}]
                    }

                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                    result = res.json()['choices'][0]['message']['content']

                    st.session_state.answers.append(user_input)
                    st.session_state.feedback.append(result)
                    st.session_state.question_index += 1
                    st.rerun()

    else:
        st.success("Interview Completed!")
        st.subheader(" Feedback Summary")

        transcript_lines = []
        for i, fb in enumerate(st.session_state.feedback):
            q_text = st.session_state.selected_questions[i]
            st.markdown(f"**Q{i+1}: {q_text}**")
            st.markdown(f"**Your Answer:** {st.session_state.answers[i]}")
            st.markdown(fb)
            st.markdown("---")

            transcript_lines.append(f"Q{i+1}: {q_text}")
            transcript_lines.append(f"User Answer: {st.session_state.answers[i]}")
            transcript_lines.append(f"{fb.strip()}")
            transcript_lines.append("-" * 50)

        transcript_text = "\n".join(transcript_lines)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"sample_transcript_{timestamp}.txt"
        with open(filename, "w") as f:
            f.write(transcript_text)

        st.success(f" Transcript saved to `{filename}`")

        with st.expander(" View Transcript"):
            st.text(transcript_text)

        if st.button("Restart"):
            st.session_state.question_index = 0
            st.session_state.answers = []
            st.session_state.feedback = []
            st.session_state.interview_started = False
            st.session_state.selected_questions = random.sample(all_questions, 5)
            st.rerun()

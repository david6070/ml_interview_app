import streamlit as st
from google import genai
import streamlit.components.v1 as components
import os
import re
from dotenv import load_dotenv

# --- Initialization & Secrets ---
load_dotenv()
try:
    api_key = st.secrets["GEMINI_API_KEY"] 
except FileNotFoundError:
    api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

# --- AI Functions ---
def generate_qa(topic, difficulty):
    """Fetches a high-quality question and answer from the AI model."""
    prompt = f"""
    You are a Senior Staff Data Scientist at a top tech company conducting an interview.
    Generate ONE highly realistic, industry-relevant interview question about {topic} at a {difficulty} level.
    The question should test practical understanding, not just textbook definitions. 
    
    Format your response EXACTLY like this:
    QUESTION: [The interview question]
    ---
    ANSWER: [A detailed, accurate, and exceptional answer that an ideal candidate would provide.]
    """
    response = client.models.generate_content(model='gemini-3.5-flash', contents=prompt)
    return response.text

def grade_response(question, ideal_answer, user_answer):
    """Acts as the interviewer grading the user's response."""
    prompt = f"""
    You are a Senior Data Scientist interviewing a candidate. 
    You asked them this question: "{question}"
    The ideal concept/answer you are looking for is: "{ideal_answer}"
    
    The candidate provided this answer: "{user_answer}"
    
    Grade their answer strictly but fairly out of 10. 
    Format your response EXACTLY like this:
    SCORE: [X/10]
    ---
    FEEDBACK: [1 to 2 short paragraphs explaining what they nailed, what they missed, and how they can improve to hit a senior industry standard.]
    """
    response = client.models.generate_content(model='gemini-3.5-flash', contents=prompt)
    return response.text

# --- UI Components ---
def inject_timer(minutes):
    """Injects a non-blocking Javascript timer into the Streamlit app."""
    seconds = minutes * 60
    timer_html = f"""
    <div id="timer" style="font-size:20px; font-weight:bold; color:#FF4B4B; padding: 10px; border: 2px solid #FF4B4B; border-radius: 8px; text-align:center; margin-bottom: 15px;">
        ⏳ Loading Timer...
    </div>
    <script>
        var timeLeft = {seconds};
        var elem = document.getElementById('timer');
        var timerId = setInterval(countdown, 1000);
        function countdown() {{
            if (timeLeft < 0) {{
                clearTimeout(timerId);
                elem.innerHTML = '🚨 Time is up! Finish your thought and submit!';
            }} else {{
                var m = Math.floor(timeLeft / 60);
                var s = timeLeft % 60;
                elem.innerHTML = '⏳ Time Remaining: ' + m + ':' + (s < 10 ? '0' : '') + s;
                timeLeft--;
            }}
        }}
    </script>
    """
    components.html(timer_html, height=70)

# --- Streamlit UI Build ---
st.set_page_config(page_title="DS/ML Interview Simulator", page_icon="🧠", layout="centered")

st.title("🧠 ML & Data Science Interview Simulator")
st.write("Generate dynamic questions, race the clock, and get graded by an AI Senior Data Scientist.")

# User inputs
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    topic = st.selectbox("Topic", ["Machine Learning Algorithms", "Deep Learning & Neural Networks", "Natural Language Processing", "A/B Testing & Statistics", "Data Engineering & SQL", "MLOps"])
with col2:
    difficulty = st.selectbox("Difficulty", ["Junior / Entry Level", "Mid-Level", "Senior / Staff Level"])
with col3:
    time_limit = st.number_input("Minutes", min_value=1, max_value=10, value=3)

# Session State Initialization
if 'question' not in st.session_state:
    st.session_state.question = None
    st.session_state.ideal_answer = None
    st.session_state.user_score = None
    st.session_state.user_feedback = None

# Generate Question Button
if st.button("Start Interview Question", type="primary"):
    with st.spinner("The interviewer is preparing your question..."):
        raw_output = generate_qa(topic, difficulty)
        
        try:
            # We use Regex (re) to safely split the text just in case the AI formats it slightly weirdly
            q_match = re.search(r"QUESTION:\s*(.*?)\s*---", raw_output, re.DOTALL)
            a_match = re.search(r"ANSWER:\s*(.*)", raw_output, re.DOTALL)
            
            st.session_state.question = q_match.group(1).strip() if q_match else "Error parsing question."
            st.session_state.ideal_answer = a_match.group(1).strip() if a_match else "Error parsing answer."
            
            # Clear previous grades when a new question is asked
            st.session_state.user_score = None
            st.session_state.user_feedback = None
        except Exception as e:
            st.error("There was an issue formatting the question. Please try generating again.")

# --- The Interview Interface ---
if st.session_state.question:
    st.divider()
    st.markdown("### 🗣️ Interviewer:")
    st.info(st.session_state.question)
    
    # Only show the timer and input if the user hasn't been graded yet
    if not st.session_state.user_score:
        inject_timer(time_limit)
        
        user_response = st.text_area("Your Answer:", height=200, placeholder="Type your answer here as if you were speaking to the interviewer...")
        
        if st.button("Submit Answer"):
            if user_response.strip() == "":
                st.warning("You can't just stare blankly at the interviewer! Type an answer.")
            else:
                with st.spinner("The interviewer is evaluating your response..."):
                    grade_raw = grade_response(st.session_state.question, st.session_state.ideal_answer, user_response)
                    
                    try:
                        score_match = re.search(r"SCORE:\s*(.*?)\s*---", grade_raw, re.DOTALL)
                        feedback_match = re.search(r"FEEDBACK:\s*(.*)", grade_raw, re.DOTALL)
                        
                        st.session_state.user_score = score_match.group(1).strip() if score_match else "N/A"
                        st.session_state.user_feedback = feedback_match.group(1).strip() if feedback_match else grade_raw
                        st.rerun() # Force a UI refresh to hide the timer and show the grade
                    except Exception as e:
                        st.error("Failed to parse the grade. Try submitting again.")

    # --- Display The Results ---
    if st.session_state.user_score:
        st.markdown("### 📊 Your Evaluation")
        
        col_score, col_feedback = st.columns([1, 3])
        with col_score:
            st.metric(label="Your Score", value=st.session_state.user_score)
        with col_feedback:
            st.write("**Feedback:**")
            st.write(st.session_state.user_feedback)
            
        st.divider()
        st.markdown("### 💡 The Ideal Answer")
        st.success(st.session_state.ideal_answer)
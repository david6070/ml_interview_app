import streamlit as st
from google import genai
import os
from dotenv import load_dotenv

# Load local .env file (for when you run it on your own Mac)
load_dotenv()

# Safely grab the API key whether we are online or local
try:
    # This is where Streamlit Cloud stores secrets
    api_key = st.secrets["GEMINI_API_KEY"] 
except FileNotFoundError:
    # Fallback to local .env file
    api_key = os.getenv("GEMINI_API_KEY")

# Initialize the GenAI client
client = genai.Client(api_key=api_key)

def generate_local_qa(topic, difficulty):
    """Return a safe offline fallback Q/A when the model is unavailable."""
    question = f"Describe a practical interview-style problem on {topic} at {difficulty} level and explain how you'd approach, evaluate, and deploy the solution."
    answer = (
        "Outline an ideal answer: define the problem, propose a modeling approach (algorithms/architecture), "+
        "discuss evaluation metrics, data requirements and potential pitfalls, include a short pseudocode or SQL example where relevant, "+
        "and finish with deployment considerations and monitoring." 
    )
    return f"QUESTION: {question}\n---\nANSWER: {answer}"


def generate_qa(topic, difficulty, max_retries=3):
    """Fetches a high-quality question and answer from the AI model with retry/backoff.

    Retries on transient server errors (like 503) with exponential backoff and jitter.
    Raises the last exception if retries are exhausted.
    """
    prompt = f"""
    You are a Senior Staff Data Scientist at a top tech company conducting an interview.
    Generate ONE highly realistic, industry-relevant interview question about {topic} at a {difficulty} level.
    The question should test practical understanding, not just textbook definitions. 
    
    Format your response EXACTLY like this:
    QUESTION: [The interview question]
    ---
    ANSWER: [A detailed, accurate, and exceptional answer that an ideal candidate would provide. Include code snippets or math where appropriate.]
    """

    backoff = 1.0
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt
            )
            return getattr(response, "text", str(response))
        except Exception as e:
            err_text = str(e)
            # Consider this a transient error if it mentions 503 or UNAVAILABLE
            transient = '503' in err_text or 'UNAVAILABLE' in err_text or 'high demand' in err_text.lower()
            if not transient:
                # Non-transient: re-raise immediately
                raise
            # If this was the last attempt, re-raise to be handled by caller
            if attempt == max_retries:
                raise
            # Sleep with exponential backoff + jitter, then retry
            time.sleep(backoff + random.random() * 0.5)
            backoff *= 2

# --- Streamlit UI Build ---
st.set_page_config(page_title="DS/ML Interview Prep", page_icon="🧠")

st.title("🧠 Industry-Level ML & Data Science Prep")
st.write("Generate dynamic, exceptional interview questions on the fly.")

# User inputs
col1, col2 = st.columns(2)
with col1:
    topic = st.selectbox("Select Topic", [
        "Machine Learning Algorithms", 
        "Deep Learning & Neural Networks", 
        "Natural Language Processing", 
        "A/B Testing & Statistics", 
        "Data Engineering & SQL",
        "Model Deployment (MLOps)"
    ])
with col2:
    difficulty = st.selectbox("Select Difficulty", ["Junior / Entry Level", "Mid-Level", "Senior / Staff Level"])

# Session state to hold the current question and answer and parsing status
if 'question' not in st.session_state:
    st.session_state.question = None
    st.session_state.answer = None
    st.session_state.raw_output = None
    st.session_state.parse_error = False
    st.session_state.show_answer = False
    st.session_state.fallback_used = False


def parse_model_output(raw_output):
    """Try several strategies to extract QUESTION and ANSWER from the raw model text."""
    if not raw_output:
        return None, None
    # 1) Look for 'QUESTION: ... --- ANSWER: ...' pattern
    m = re.search(r"QUESTION:\s*(.*?)\s*---\s*ANSWER:\s*(.*)", raw_output, re.S | re.I)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    # 2) Look for 'QUESTION: ... ANSWER: ...' without the separator
    m2 = re.search(r"QUESTION:\s*(.*?)\s*ANSWER:\s*(.*)", raw_output, re.S | re.I)
    if m2:
        return m2.group(1).strip(), m2.group(2).strip()
    # 3) JSON fallback
    try:
        j = json.loads(raw_output)
        q = j.get('question') or j.get('QUESTION') or j.get('prompt')
        a = j.get('answer') or j.get('ANSWER') or j.get('response')
        if q and a:
            return str(q).strip(), str(a).strip()
    except Exception:
        pass
    # 4) Last-resort: try simple split on '---' like before
    try:
        q_part, a_part = raw_output.split("---", 1)
        return q_part.replace("QUESTION:", "").strip(), a_part.replace("ANSWER:", "").strip()
    except Exception:
        return None, None


if st.button("Generate New Question"):
    with st.spinner("Consulting the Senior Data Scientist..."):
        try:
            raw_output = generate_qa(topic, difficulty)
            st.session_state.fallback_used = False
        except Exception as e:
            # If the model is unavailable, surface a friendly message and use the local fallback
            err_text = str(e)
            st.warning("Model unavailable or returned an error — using offline fallback.\n" + err_text)
            raw_output = generate_local_qa(topic, difficulty)
            st.session_state.fallback_used = True

        st.session_state.raw_output = raw_output
        q, a = parse_model_output(raw_output)
        if q and a:
            st.session_state.question = q
            st.session_state.answer = a
            st.session_state.parse_error = False
            st.session_state.show_answer = False
        else:
            st.session_state.question = None
            st.session_state.answer = None
            st.session_state.parse_error = True

# Display logic
if st.session_state.question:
    st.markdown("### 📝 Question:")
    st.info(st.session_state.question)

    # Reveal the answer with a checkbox so we don't trigger a rerun unintentionally
    show = st.checkbox("Show Answer", value=st.session_state.show_answer)
    st.session_state.show_answer = show
    if st.session_state.show_answer:
        st.markdown("### 💡 Ideal Answer:")
        st.success(st.session_state.answer)

# If there was a parsing problem, show the raw output and offer a regenerate button
if st.session_state.parse_error:
    st.error("There was an issue parsing the model output. You can view the raw output and try regenerating.")
    with st.expander("Raw model output"):
        st.code(st.session_state.raw_output or "(no output captured)")
    if st.button("Regenerate"):
        with st.spinner("Retrying generation..."):
            try:
                raw_output = generate_qa(topic, difficulty)
                st.session_state.fallback_used = False
            except Exception as e:
                err_text = str(e)
                st.warning("Model unavailable or returned an error — using offline fallback.\n" + err_text)
                raw_output = generate_local_qa(topic, difficulty)
                st.session_state.fallback_used = True

            st.session_state.raw_output = raw_output
            q, a = parse_model_output(raw_output)
            if q and a:
                st.session_state.question = q
                st.session_state.answer = a
                st.session_state.parse_error = False
                st.session_state.show_answer = False
            else:
                st.session_state.parse_error = True
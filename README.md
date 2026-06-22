# 🧠 ML & Data Science Interview Simulator

An interactive, AI-powered web application designed to help Data Scientists and Machine Learning Engineers prepare for industry-standard technical interviews. Built using **Python**, **Streamlit**, and the **Google GenAI SDK (Gemini API)**.

## 🔗 Live Demo
Try out the simulator here: [Live App on Streamlit Cloud](https://mlinterviewapp-apdxnvvrdfdb6waqji8r8b.streamlit.app/)

---

## ✨ Features

- **Dynamic Q&A Generation:** Acts as a Senior Staff Data Scientist to generate realistic, scenario-based interview questions tailored across various domains (ML Algorithms, Deep Learning, NLP, A/B Testing, MLOps, SQL) and difficulties (Junior to Senior Level).
- **Interactive Evaluation:** Candidates can type their responses directly into the simulator to test their communication and problem-solving skills under pressure.
- **AI-Powered Grading:** Leverages the Gemini API to analyze the candidate's input, score the response out of 10, offer granular feedback on areas of improvement, and reveal the optimal industry-standard solution.
- **Embedded Visual Timer:** Uses custom injected JavaScript/HTML components to provide a non-blocking countdown timer, maintaining synchronization without interrupting Streamlit's UI performance.

---

## 🛠️ Tech Stack & Architecture

- **Frontend & App Framework:** Streamlit (v1.58.0)
- **AI Core:** Google GenAI SDK (`gemini-3.5-flash`)
- **Environment Management:** Python venv, `python-dotenv`
- **Text Processing & Parsing:** Python Regular Expressions (`re`)
- **Deployment & Infrastructure:** GitHub, Streamlit Community Cloud

---

## 🚀 The Development Journey: Step-by-Step

### 1. Local Environment & Base Build
- Formulated the core architecture using Python.
- Configured local environment variables (`.env`) to safely secure the Google Gemini API keys.
- Implemented structured Prompt Engineering to ensure the LLM outputs strictly consistent, parsable syntax (`QUESTION: ... --- ANSWER: ...`).

### 2. Version Control Architecture
- Configured Git version control locally on macOS.
- Solved initial local state issues by aligning Git branches and initializing a standard `main` branch tracking configuration.
- Linked the local repository to the remote origin on GitHub (`david6070/ml_interview_app`).

### 3. CI/CD Cloud Deployment
- Deployed the application to **Streamlit Community Cloud** directly hooked to the GitHub repository's main branch for automated continuous deployment.
- Configured secure runtime secrets inside Streamlit Cloud's dashboard to provision the `GEMINI_API_KEY` dynamically using `st.secrets`, bypassing the hidden local `.env` configuration.

### 4. Advanced Interactivity & Edge-Case Engineering
- **Asynchronous UI Injections:** Implemented a JavaScript-based visual timer inside an HTML component to bypass Streamlit's traditional synchronous loop execution, allowing users to type without locking the layout.
- **Parsing Robustness:** Integrated rigorous regular expression parsing logic to cleanly split AI responses into UI components, troubleshooting and resolving runtime execution issues like uncaught `NameError` types during the import structure.
- **Rate Limit Handlers:** Handled cloud-based `ClientError (429 Resource Exhausted)` errors natively by documenting free-tier API limitations gracefully in the deployment presentation.

---

## 💻 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/david6070/ml_interview_app.git](https://github.com/david6070/ml_interview_app.git)
   cd ml_interview_app
import os
import json
import logging
from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Flask App Setup
class Base(DeclarativeBase): pass

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Question Definitions
questions = [
    {
        "id": 1,
        "text": "How do you prefer to structure your workday?",
        "task-id": "work-style",
        "is_free_response": False,
        "options": [("A", "Structured schedule"), ("B", "Flexible work hours")]
    },
    {
        "id": 2,
        "text": "What type of workspace do you find most comfortable?",
        "task-id": "environment",
        "is_free_response": False,
        "options": [("A", "Quiet/private spaces"), ("B", "Collaborative/open spaces")]
    },
    {
        "id": 3,
        "text": "How comfortable are you with frequent interactions with colleagues?",
        "task-id": "interaction-level",
        "is_free_response": False,
        "options": [("A", "Minimal"), ("B", "Regular teamwork"), ("C", "Leading teams")]
    },
    {
        "id": 4,
        "text": "Do you prefer tasks that are:",
        "task-id": "task-preference",
        "is_free_response": False,
        "options": [("A", "Detailed and focused"), ("B", "Creative and innovative")]
    },
    {
        "id": 5,
        "text": "What else would you like us to know about your desired work environment?",
        "task-id": "free-response",
        "is_free_response": True,
        "options": []
    }
]

@app.route("/")
def welcome():
    session.clear()
    return render_template("welcome.html")

@app.route("/question/<int:question_id>", methods=["GET", "POST"])
def question(question_id):
    if not (1 <= question_id <= len(questions)):
        return redirect(url_for("welcome"))

    if request.method == "POST":
        answer = request.form.get("answer")
        if answer:
            session[f"q{question_id}"] = answer.strip()
            if question_id < len(questions):
                return redirect(url_for("question", question_id=question_id + 1))
            return redirect(url_for("results"))

    question_obj = questions[question_id - 1]
    progress = (question_id / len(questions)) * 100
    return render_template("question.html", question=question_obj, progress=progress)

@app.route("/results")
def results():
    if not all(f"q{i+1}" in session for i in range(len(questions))):
        return redirect(url_for("welcome"))

    try:
        profile_key = "-".join(session[f"q{i+1}"] for i in range(4))

        with open("personality_analyses.json") as f:
            profiles = json.load(f)

        profile_data = profiles.get(profile_key)
        if not profile_data:
            raise ValueError(f"Missing profile for key: {profile_key}")

        analysis_html = format_analysis_html(profile_data["analysis"])

        from rag_engine import load_vectorstore_mock, get_semantic_matches
        vectorstore = load_vectorstore_mock()
        matched_jobs = get_semantic_matches(session["q5"], vectorstore)
        recommendations = format_rag_jobs(matched_jobs)

        return render_template("results.html", analysis=analysis_html, recommendations=recommendations)

    except Exception as e:
        logging.error(f"Error generating results: {e}")
        return "Something went wrong generating your results. Please try again."

def format_analysis_html(analysis):
    return f"""
    <div class='analysis-section'>
        <h3>Work Style</h3>
        <p><strong>{analysis['work_style']['description']}</strong></p>
        <p>{analysis['work_style']['explanation']}</p>

        <h3>Ideal Environment</h3>
        <p><strong>{analysis['environment']['description']}</strong></p>
        <p>{analysis['environment']['explanation']}</p>

        <h3>Interaction Level</h3>
        <p><strong>{analysis['interaction_level']['description']}</strong></p>
        <p>{analysis['interaction_level']['explanation']}</p>

        <h3>Task Preferences</h3>
        <p><strong>{analysis['task_preference']['description']}</strong></p>
        <p>{analysis['task_preference']['explanation']}</p>

        <h3>Accommodations</h3>
        <p><strong>{analysis['accommodations']['description']}</strong></p>
        <p>{analysis['accommodations']['explanation']}</p>
    </div>
    """

def format_rag_jobs(rag_results):
    return [
        {
            "title": job["title"],
            "company": job["company"],
            "location": "Remote or Hybrid",
            "match_score": job["score"],
            "reasoning": f"Semantic match based on your preferences.",
            "url": job["url"]
        } for job in rag_results
    ]

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

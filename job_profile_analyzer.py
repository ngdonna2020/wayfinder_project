import os
import json
from openai import OpenAI
import logging
from dotenv import load_dotenv
import sqlite3
from typing import Dict, List, Tuple

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Questions from app.py (same as used for user profiles)
questions = [
    {
        "id": 1,
        "text": "How do you prefer to structure your workday?",
        "options": [
            ("A", "I thrive with a structured schedule"),
            ("B", "I prefer flexibility in my work hours")
        ]
    },
    {
        "id": 2,
        "text": "What type of workspace do you find most comfortable?",
        "options": [
            ("A", "Quiet and private spaces"),
            ("B", "Collaborative and open spaces")
        ]
    },
    {
        "id": 3,
        "text": "How comfortable are you with frequent interactions with colleagues?",
        "options": [
            ("A", "Prefer minimal interactions"),
            ("B", "Comfortable with regular teamwork"),
            ("C", "Enjoy leading or coordinating teams")
        ]
    },
    {
        "id": 4,
        "text": "Do you prefer tasks that are:",
        "options": [
            ("A", "Highly detailed and focused"),
            ("B", "Creative and innovative")
        ]
    }
]

def analyze_job_description(job_description: str) -> str:
    """Analyze a job description to determine its profile match"""
    prompt = f"""
    Based on the following job description, determine which profile combination (A-A-A-A format) best matches the job's requirements.
    Consider these aspects:
    1. Work schedule structure (A: structured, B: flexible)
    2. Workspace type (A: quiet/private, B: collaborative/open)
    3. Interaction level (A: minimal, B: regular teamwork, C: leading/coordinating)
    4. Task type (A: detailed/focused, B: creative/innovative)

    Return ONLY the profile combination (e.g., "A-A-A-A") that best matches the job description.

    Job Description:
    {job_description}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error analyzing job description: {e}")
        return None

def create_database():
    """Create SQLite database for storing profiles and job matches"""
    conn = sqlite3.connect('job_profiles.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS profiles (
        profile_id TEXT PRIMARY KEY,
        work_style TEXT,
        environment TEXT,
        interaction_level TEXT,
        task_preference TEXT,
        accommodations TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        job_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        company TEXT,
        description TEXT,
        profile_id TEXT,
        FOREIGN KEY (profile_id) REFERENCES profiles (profile_id)
    )
    ''')
    
    conn.commit()
    return conn

def load_profiles(conn: sqlite3.Connection):
    """Load profiles from the generated JSON file into the database"""
    try:
        with open('personality_analyses.json', 'r') as f:
            profiles = json.load(f)
            
        cursor = conn.cursor()
        for profile_id, data in profiles.items():
            analysis = data['analysis']
            cursor.execute('''
            INSERT OR REPLACE INTO profiles 
            (profile_id, work_style, environment, interaction_level, task_preference, accommodations)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                profile_id,
                json.dumps(analysis['work_style']),
                json.dumps(analysis['environment']),
                json.dumps(analysis['interaction_level']),
                json.dumps(analysis['task_preference']),
                json.dumps(analysis['accommodations'])
            ))
        
        conn.commit()
        logger.info("Successfully loaded profiles into database")
    except Exception as e:
        logger.error(f"Error loading profiles: {e}")

def analyze_and_store_jobs(conn: sqlite3.Connection, jobs: List[Dict]):
    """Analyze job descriptions and store them in the database"""
    cursor = conn.cursor()
    
    for job in jobs:
        profile_id = analyze_job_description(job['description'])
        if profile_id:
            cursor.execute('''
            INSERT INTO jobs (title, company, description, profile_id)
            VALUES (?, ?, ?, ?)
            ''', (job['title'], job['company'], job['description'], profile_id))
    
    conn.commit()
    logger.info("Successfully analyzed and stored jobs")

def main():
    # Create and initialize database
    conn = create_database()
    load_profiles(conn)
    
    # Sample jobs to analyze (replace with actual job data)
    sample_jobs = [
        {
            "title": "Data Quality Analyst",
            "company": "Oracle",
            "description": "Looking for a detail-oriented analyst who thrives in a structured environment. The role requires working independently with minimal supervision, focusing on data quality and accuracy. The position offers a flexible work schedule and remote work options."
        },
        {
            "title": "Creative Director",
            "company": "Design Studio",
            "description": "Seeking a creative leader to manage a team of designers. The role involves frequent collaboration, team meetings, and client interactions. The position requires innovative thinking and the ability to work in a dynamic, open office environment."
        }
    ]
    
    # Analyze and store jobs
    analyze_and_store_jobs(conn, sample_jobs)
    
    # Close database connection
    conn.close()

if __name__ == "__main__":
    main() 
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, session, redirect
from supabase import create_client, Client

app = Flask(__name__, 
            template_folder='../templates', 
            static_folder='../static')

# Set a secret key for sessions (Vercel will use your environment variable)
app.secret_key = os.environ.get("SECRET_KEY", "P6.zSvdn7ZMYw-c")

app.permanent_session_lifetime = timedelta(minutes=60)

# 1. Use the fixed environment variable
app.secret_key = os.environ.get("SECRET_KEY", "fallback-dev-key")

# 2. Force strict cookie settings for Vercel
app.config.update(
    SESSION_COOKIE_SECURE=True,   # Required for HTTPS
    SESSION_COOKIE_HTTPONLY=True, # Security best practice
    SESSION_COOKIE_SAMESITE='Lax',# Allows the redirect to work
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=60)
)

# --- SUPABASE SETUP ---
# These are pulled automatically from your Vercel + Supabase integration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@dataclass
class UserRecord:
    full_name: str
    school_name: str
    email: str
    started_at: str
    score: int = 0

# --- QUIZ DATA ---
QUIZ_DATA = [
    {
        "q": "You have a filing cabinet with 1,000,000 folders...",
        "options": [
            {"text": "Open the middle, check if before/after...", "correct": True, "note": "Binary Search..."},
            {"text": "Start at the first folder...", "correct": False, "note": "Linear Search..."},
            {"text": "Pick random drawers...", "correct": False, "note": "Randomness..."}
        ]
    },
    {
        "q": "A robot finds its way out of a maze. Which logic ensures it finds the exit?",
        "options": [
            {"text": "Always keep your right hand touching a wall.", "correct": True, "note": "The Wall Follower rule ensures you explore the boundary."},
            {"text": "Walk forward until you hit a wall, then turn randomly.", "correct": False, "note": "Random turns can lead to infinite loops."}
        ]
    },
    {
        "q": "Alarm requirement: 'Master Key ON' AND ('Button A' OR 'Button B'). If Key is OFF but both buttons are pressed, what happens?",
        "options": [
            {"text": "The alarm stays silent.", "correct": True, "note": "The 'AND' gate failed because the Key was OFF."},
            {"text": "The alarm goes off.", "correct": False, "note": "The Master Key is a mandatory gatekeeper."}
        ]
    },
    {
        "q": "If doubling the work makes the time jump from 10s to 40s, what does this tell you?",
        "options": [
            {"text": "The process gets significantly slower as it scales up.", "correct": True, "note": "This is non-linear (Quadratic) growth."},
            {"text": "The process is perfectly efficient.", "correct": False, "note": "Efficiency would be a linear 20s."}
        ]
    },
    {
        "q": "If a box holds 4 items and you force a 5th one in, what happens in a typical system?",
        "options": [
            {"text": "The system overflows and likely crashes.", "correct": True, "note": "Buffer overflows are a major security and stability risk."},
            {"text": "The box grows larger on its own.", "correct": False, "note": "Hardware needs explicit instructions to reallocate memory."}
        ]
    }
    # ... add your other 4 questions here ...
]

# --- PAGE ROUTES ---

@app.route('/')
def home():
    # Landing page with the registration form (form.html)
    return render_template('form.html')

@app.route('/quiz')
def quiz_page():
    # Only allow access if user has submitted the form
    if 'user_info' not in session:
        return redirect('/')
    return render_template('index.html')

# --- API ROUTES ---

@app.route('/api/questions')
def get_questions():
    return jsonify(QUIZ_DATA)

@app.route('/api/user', methods=['GET', 'POST']) # Added GET
def register_user():
    if request.method == 'POST':
        data = request.json
        
        # Validation to prevent empty records
        if not data or not data.get('email'):
            return jsonify({"error": "Missing data"}), 400

        user_record = UserRecord(
            full_name=data.get('full_name'),
            school_name=data.get('school_name'),
            email=data.get('email'),
            started_at=datetime.utcnow().isoformat()
        )

        try:
            # 1. Save to Supabase
            supabase.table('scores').insert(asdict(user_record)).execute()
            
            # 2. Setup Session
            session.permanent = True
            session['user_info'] = asdict(user_record)
            session.modified = True
            
            return jsonify({"status": "success"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # Handle GET request (optional, for checking session)
    return jsonify(session.get('user_info', {}))

@app.route('/api/submit-score', methods=['POST'])
@app.route('/api/submit-score', methods=['POST'])
def submit_score():
    if 'user_info' not in session:
        return jsonify({"error": "No active session found"}), 401
    
    data = request.json
    final_score = data.get('score')
    
    # Get the specific details from the session
    user_email = session['user_info']['email']
    started_at = session['user_info']['started_at'] # This is the unique "ID" for this session

    try:
        # We filter by BOTH email AND the exact start time 
        # so we only update the single row created at the start of this quiz
        supabase.table('scores') \
            .update({"score": final_score}) \
            .eq('email', user_email) \
            .eq('started_at', started_at) \
            .execute()
        
        return jsonify({"status": "Score saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# No app.run() needed for Vercel!

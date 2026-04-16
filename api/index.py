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
        "q": "You have a filing cabinet with 1,000,000 folders. What is the fastest way to locate a single folder if the list is sorted?",
        "options": [
            {"text": "Start at the first folder and go one by one.", "correct": False, "note": "That would be linear search and too slow for a million items."},
            {"text": "Open the middle, check if it's before/after, then repeat.", "correct": True, "note": "Binary search works well on sorted collections."},
            {"text": "Pick random drawers until you find it.", "correct": False, "note": "Random search is inefficient and unreliable."},
            {"text": "Split the cabinet into two halves and search both at once.", "correct": False, "note": "The idea is close, but binary search is the specific correct method."}
        ]
    },
    {
        "q": "A robot finds its way out of a maze. Which logic ensures it will eventually exit?",
        "options": [
            {"text": "Keep moving straight and hope the exit appears.", "correct": False, "note": "This does not guarantee maze exit."},
            {"text": "Always keep your right hand touching a wall.", "correct": False, "note": "This works only for simple mazes with one boundary."},
            {"text": "Randomly choose a direction at each intersection.", "correct": False, "note": "Random moves can lead to loops and do not guarantee exit."},
            {"text": "Use a systematic wall-follower strategy to explore the boundary.", "correct": True, "note": "Wall following explores the maze boundary consistently."}
        ]
    },
    {
        "q": "Alarm requirement: 'Master Key ON' AND ('Button A' OR 'Button B'). If Key is OFF but both buttons are pressed, what happens?",
        "options": [
            {"text": "The alarm stays silent.", "correct": False, "note": "The AND condition requires the Master Key to be ON."},
            {"text": "The alarm goes off.", "correct": False, "note": "Without the Master Key ON, the AND condition fails."},
            {"text": "The alarm remains off because the Master Key is OFF.", "correct": True, "note": "Both button inputs matter, but the Master Key gate is mandatory."},
            {"text": "The buttons override the Master Key and trigger the alarm.", "correct": False, "note": "The logical requirement prevents button-only triggering."}
        ]
    },
    {
        "q": "If doubling the work makes the time jump from 10s to 40s, what does this tell you about the process?",
        "options": [
            {"text": "It is a linear process with perfect efficiency.", "correct": False, "note": "Linear scaling would double the time from 10s to 20s."},
            {"text": "The process becomes twice as fast.", "correct": False, "note": "The time increasing means it is not faster."},
            {"text": "It is growing quadratically or worse.", "correct": True, "note": "A jump from 10s to 40s when doubling work suggests non-linear scaling."},
            {"text": "It only works for small inputs, not for larger ones.", "correct": False, "note": "This might be true in general, but the time pattern points to quadratic growth."}
        ]
    },
    {
        "q": "If a box holds 4 items and you force a 5th one in, what typically happens in a system?",
        "options": [
            {"text": "The fifth item is stored and everything is fine.", "correct": False, "note": "Most fixed-size containers cannot automatically accept extra items."},
            {"text": "The box grows larger to fit the item.", "correct": False, "note": "Dynamic resizing requires explicit logic, not automatic growth."},
            {"text": "The system overflows and likely crashes.", "correct": False, "note": "This is one possible failure mode but not always the specific behaviour."},
            {"text": "It overflows and triggers an error or failure condition.", "correct": True, "note": "Buffer or capacity overflow usually leads to errors or crashes if not handled."}
        ]
    }
]

# --- PAGE ROUTES ---

@app.route('/')
def welcome_page():
    return render_template('welcome.html', user_info=session.get('user_info'))

@app.route('/register')
def register_page():
    if 'user_info' in session and not session.get('attempted', False):
        return redirect('/quiz')
    if session.get('attempted', False):
        return redirect('/')
    return render_template('form.html')

@app.route('/quiz')
def quiz_page():
    # Only allow access if user has submitted the form
    if 'user_info' not in session:
        return redirect('/register')
    if session.get('attempted', False):
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
            session['attempted'] = False
            session.modified = True
            
            return jsonify({"status": "success"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # Handle GET request (optional, for checking session)
    return jsonify(session.get('user_info', {}))

@app.route('/api/submit-score', methods=['POST'])
def submit_score():
    if 'user_info' not in session:
        return jsonify({"error": "No active session found"}), 401
    
    data = request.json
    final_score = data.get('score')
    responses = data.get('responses', [])

    if final_score is None:
        return jsonify({"error": "Score is required"}), 400
    if not isinstance(responses, list):
        return jsonify({"error": "Responses must be an array"}), 400
    
    # Get the specific details from the session
    user_email = session['user_info']['email']
    started_at = session['user_info']['started_at'] # This is the unique "ID" for this session

    try:
        # We filter by BOTH email AND the exact start time 
        # so we only update the single row created at the start of this quiz
        supabase.table('scores') \
            .update({"score": final_score, "responses": responses}) \
            .eq('email', user_email) \
            .eq('started_at', started_at) \
            .execute()
        
        session['attempted'] = True
        session.modified = True
        return jsonify({"status": "Score saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_session():
    session.clear()
    return jsonify({"status": "reset"}), 200

# No app.run() needed for Vercel!

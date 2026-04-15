from dataclasses import asdict, dataclass
from datetime import datetime
from flask import Flask, render_template, jsonify, request, session, redirect

app = Flask(__name__, 
            template_folder='../templates', 
            static_folder='../static')
app.secret_key = 'dev-secret-key'  # replace with a secure secret in production

# Placeholder storage for user data until a real database is configured
USER_SUBMISSIONS = []

@dataclass
class UserRecord:
    full_name: str
    school_name: str
    email: str
    started_at: str

# The quiz data moved to the backend
QUIZ_DATA = [
    {
        "q": "You have a filing cabinet with 1,000,000 folders, organized alphabetically. Which method is most efficient to find one specific folder?",
        "options": [
            {"text": "Open the middle, check if before/after, and repeat splitting in half.", "correct": True, "note": "This is Binary Search—the gold standard for sorted data."},
            {"text": "Start at the first folder and check every single one.", "correct": False, "note": "This is Linear Search; it's $O(n)$ and too slow here."},
            {"text": "Pick random drawers and hope you get lucky.", "correct": False, "note": "Randomness isn't a reliable algorithm."}
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
]

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/quiz')
def quiz():
    if 'user_info' not in session:
        return redirect('/')
    return render_template('index.html')

def save_user_record(user: UserRecord):
    # This is a temporary placeholder for database persistence.
    USER_SUBMISSIONS.append(asdict(user))
    return user

@app.route('/api/user', methods=['GET', 'POST'])
def save_user():
    if request.method == 'GET':
        user_info = session.get('user_info')
        if not user_info:
            return jsonify({'error': 'User info not found.'}), 404
        return jsonify(user_info)

    payload = request.get_json() or {}
    full_name = payload.get('full_name', '').strip()
    school_name = payload.get('school_name', '').strip()
    email = payload.get('email', '').strip()

    if not full_name or not school_name or not email:
        return jsonify({'error': 'Full name, school name, and email are required.'}), 400

    user = UserRecord(full_name=full_name,
                      school_name=school_name,
                      email=email,
                      started_at=datetime.utcnow().isoformat())
    session['user_info'] = asdict(user)
    save_user_record(user)
    return jsonify(session['user_info'])

@app.route('/api/questions')
def get_questions():
    return jsonify(QUIZ_DATA)

if __name__ == "__main__":
    app.run(debug=True)
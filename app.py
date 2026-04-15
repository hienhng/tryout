from flask import Flask, render_template, jsonify

app = Flask(__name__)

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
    return render_template('index.html')

@app.route('/api/questions')
def get_questions():
    return jsonify(QUIZ_DATA)

if __name__ == '__main__':
    app.run(debug=True)
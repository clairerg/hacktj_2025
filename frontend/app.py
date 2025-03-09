from flask import Flask, render_template, request, jsonify
import sqlite3
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect("congress_data.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE name LIKE ?", (f"%{query}%",))
    results = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if any(r['name'] == 'Donald Trump' for r in results) == False:
        results.append({'name': 'Donald Trump', 'position': 'Former President', 'party': 'Republican'})
    return results

@app.route('/candidate/<string:candidate_id>')
def candidate_detail(candidate_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE id = ?", (candidate_id,))
    candidate = cursor.fetchone()
    conn.close()
    if candidate:
        return render_template('candidate.html', candidate=dict(candidate))
    return "Candidate not found", 404

def load_summaries():
    summaries_dir = "../summaries"
    summary_data = []

    for filename in sorted(os.listdir(summaries_dir)):
        if filename.startswith("summary_") and filename.endswith(".txt"):
            with open(os.path.join(summaries_dir, filename), "r") as file:
                summary_data.append({"filename": filename, "content": file.read().strip()})

    return summary_data

@app.route('/summaries')
def show_summaries():
    summaries = load_summaries()
    return render_template('summaries.html', summaries=summaries)


if __name__ == '__main__':
    app.run(debug=True)
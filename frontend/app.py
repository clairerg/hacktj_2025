from flask import Flask, render_template, request, jsonify
import sqlite3
from flask_cors import CORS

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
    return jsonify(results)

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

if __name__ == '__main__':
    app.run(debug=True)
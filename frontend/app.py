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
    return results

@app.route('/reverse_search', methods=['GET'])
def reverse_search():
    policies = request.args.getlist('policies')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT DISTINCT members.* FROM members
        JOIN bills ON members.id = bills.member_id
        WHERE bills.policy_area IN top_policies
    """, policies)
    results = cursor.fetchall()
    conn.close()
    return render_template('reverse_search.html', results=results, policies=policies)

if __name__ == '__main__':
    app.run(debug=True)

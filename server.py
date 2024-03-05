from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

DATABASE = './seent.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/tokens', methods=['GET'])
def get_tokens():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM token_data LIMIT ? OFFSET ?', (per_page, offset))
    rows = cur.fetchall()

    tokens = [dict(row) for row in rows]

    cur.close()
    conn.close()

    return jsonify(tokens)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, redirect, request, url_for, render_template
from flask_socketio import SocketIO
import sqlite3
import os

app = Flask(__name__)

DATABASE = './seent.db'
DEBUG=False
socketio = SocketIO(app)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return redirect(url_for('get_tokens'))

@app.route('/tokens')
def get_tokens():
    search_query = request.args.get('query', '')

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'asc')
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cur = conn.cursor()

    if search_query:
        cur.execute(f"SELECT * FROM token_data WHERE name LIKE ? ORDER BY {sort_by} {sort_order}", ('%' + search_query + '%',))
    else:
        cur.execute(f'SELECT * FROM token_data ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?', (per_page, offset))

    rows = cur.fetchall()
    tokens = [dict(row) for row in rows]

    cur.close()
    conn.close()

    return render_template('list_view.html', tokens=tokens, sort_by=sort_by, sort_order=sort_order)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=DEBUG)

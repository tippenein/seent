from flask import Flask, redirect, request, url_for, render_template, jsonify
import sqlite3
import requests
import json

app = Flask(__name__)

DATABASE = './seent.db'


def mkBirdeyeUrl(token):
   return 'https://public-api.birdeye.so/public/price?address=' + token

# response = requests.get(url)

# print(response.text)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return redirect(url_for('get_tokens'))

@app.route('/data', methods=['GET'])
def get_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT json_blob FROM json_data ORDER BY id DESC LIMIT 1;')  # Assuming you want the latest entry
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify(row['json_blob'])
    else:
        return jsonify({"error": "No data found"}), 404

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

    cur.execute('SELECT json_blob FROM json_data ORDER BY id DESC LIMIT 1;')  # Assuming you want the latest entry
    row = cur.fetchone()

    conn.close()
    if row:
        ticker_data = row['json_blob']
    else:
        return jsonify({"error": "No data found"}), 404
    tickers = json.loads(ticker_data)
    # for some reason the ticker_id is segmented into <real>_<something else> so we just take the first part and index on that
    transformed_tickers = {key.split('_')[0]: value for key, value in tickers.items()}
    return render_template('list_view.html', tokens=tokens, sort_by=sort_by, sort_order=sort_order, ticker_data=transformed_tickers, floatConv=float)

if __name__ == '__main__':
    app.run(debug=True)

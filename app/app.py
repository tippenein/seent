import base64
from flask import jsonify, Flask, redirect, request, url_for, render_template, send_file, send_from_directory
import sqlite3
import os
from datetime import datetime
from .plot import datetime_to_epoch, get_solana_pool_address, plot_ohlc_data
from .db import DATABASE_CONFIG, DATABASE_TYPE, DatabaseController
from .token import fetch_token_data
app = Flask(__name__)

DEBUG=False

DB_TIME_FORMAT='%Y-%m-%d %H:%M:%S'
READABLE_TIME_FORMAT= '%b %d %H:%M'

ENV = os.getenv('ENV')
db = DatabaseController(DATABASE_CONFIG[DATABASE_TYPE], DATABASE_TYPE)

def format_currency(value):
    if value:
        return "{:,.2f}".format(value)

def format_number(value):
    if value:
        return "{:,}".format(value)

def format_whole(value):
    if value is not None:
        return "{:,}".format(int(value))

app.jinja_env.filters['format_number'] = format_number
app.jinja_env.filters['format_currency'] = format_currency
app.jinja_env.filters['format_whole'] = format_whole

# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'app/static'),
#                                'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/health')
def health():
    return jsonify(healthy=True)

@app.route('/')
def home():
    top_signals = ['3psH1Mj1f7yUfaD5gh6Zj7epE8hhrMkMETgv5TshQA4o',
                   'Av6qVigkb7USQyPXJkUvAEm4f599WTRvd75PUWBA9eNm',
                   'GRFKaABC518SqXMvBpAVYUZtVT3Nj4mYk7E7xU4gA5Rg',
                   'Bf6xK9vFfKqUW6844zHQz9oq689nDZqizugxT5patYBy',
                   '7bQsj9DciGXs6cTkhB3D1WbcEjuMpmD7amQRWjEVBpu',
                   'ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82',
                   'D8r8XTuCrUhLheWeGXSwC3G92RhASficV3YA7B2XWcLv']

    query = "SELECT * FROM token_data WHERE token IN ({})".format(', '.join(['?' if DATABASE_TYPE == 'sqlite' else '%s'] * len(top_signals)))
    tokens = db.query_db(query, top_signals)

    # Filter the list of tokens to keep only the latest row for each token
    latest_tokens = {}
    for token in tokens:
        if token['token'] not in latest_tokens or token['date'] > latest_tokens[token['token']]['date']:
            latest_tokens[token['token']] = token

    tokens = list(latest_tokens.values())

    current = fetch_token_data([token['token'] for token in tokens])

    def datetime_friendly(dt):
        datetime_obj = datetime.strptime(dt, DB_TIME_FORMAT)
        return {'readable': datetime_obj.strftime(READABLE_TIME_FORMAT), 'dt': datetime_obj}

    return render_template('home.html',
                           tokens=tokens,
                           current=current,
                           datetime_friendly=datetime_friendly,
                           float=float)

@app.route('/tokens')
def get_tokens():
    search_query = request.args.get('query', '')
    print(request.args)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'desc')
    ai_degen = request.args.get('ai_degen', None)
    offset = (page - 1) * per_page

    def datetime_friendly(dt):
        datetime_obj = datetime.strptime(dt, DB_TIME_FORMAT)

        return {'readable': datetime_obj.strftime(READABLE_TIME_FORMAT), 'dt': datetime_obj}

    summary = db.query_db("""SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN ai_degen = 'green' THEN 1 ELSE 0 END) AS green,
        SUM(CASE WHEN ai_degen = 'red' THEN 1 ELSE 0 END) AS red,
        SUM(CASE WHEN ai_degen = 'yellow' THEN 1 ELSE 0 END) AS yellow,
        AVG(marketcap) AS average_marketcap,
        (SELECT ROUND(AVG(daily_count)) FROM (
            SELECT COUNT(*) AS daily_count
            FROM token_data
            GROUP BY DATE(date)
        ) as sub_query) AS average_entries_per_day
        FROM
        token_data""", {})

    if search_query:
        parameters = {'search_query': f"%{search_query}%"}
        if ENV == 'dev':
            query = f"SELECT * FROM token_data WHERE name LIKE :search_query"
        else:
            query = f"SELECT * FROM token_data WHERE name ILIKE %(search_query)s"
    else:
        parameters = {'limit': per_page, 'offset': offset }

        where_clause = ""
        if ai_degen is not None:
            parameters['ai_degen'] = ai_degen
            where_clause = "where ai_degen = "
            if ENV == 'dev':
                where_clause += ":ai_degen"
            else:
                where_clause += "%(ai_degen)s"
        if ENV == 'dev':
            query = f"SELECT * FROM token_data {where_clause} order by {sort_by} {sort_order} LIMIT :limit OFFSET :offset"
        else:
            query = f"SELECT * FROM token_data {where_clause} order by {sort_by} {sort_order} NULLS LAST LIMIT %(limit)s OFFSET %(offset)s"

    tokens = db.query_db(query, parameters)

    current = fetch_token_data([token['token'] for token in tokens])

    prev_page_url = url_for('get_tokens', page=page-1, query=search_query, ai_degen=ai_degen) if page > 1 else None
    next_page_url = url_for('get_tokens', page=page+1, query=search_query, ai_degen=ai_degen)

    return render_template('list_view.html',
                            tokens=tokens,
                            current=current,
                            summary=summary[0],
                            sort_by=sort_by,
                            sort_order=sort_order,
                            datetime_friendly=datetime_friendly,
                            prev_page_url=prev_page_url,
                            next_page_url=next_page_url,
                            page=page,
                            float=float,
                            ai_degen=ai_degen
                            )

@app.route('/tokens/<token>/<date>')
def token_detail(token, date):
    dt = 0
    bot_timestamp = int(datetime_to_epoch(date) - dt)
    pool_address = get_solana_pool_address(token)
    if pool_address is not None:
        image = plot_ohlc_data(pool_address, bot_timestamp)
        if image is not None:
            # Encode the image bytes to base64
            image_base64 = base64.b64encode(image[0]).decode('utf-8')
            return render_template('plot.html', token=token, image=image_base64)
    else:
        print("shit")
        return render_template('404.html', message=f"Could not find {token}")

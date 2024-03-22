import base64
from flask import jsonify, Flask, redirect, request, url_for, render_template, send_file, send_from_directory
import sqlite3
import os
from datetime import datetime
from .plot import datetime_to_epoch, get_solana_pool_address, plot_ohlc_data
from .db import DATABASE_CONFIG, DATABASE_TYPE, DatabaseController

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

app.jinja_env.filters['format_number'] = format_number
app.jinja_env.filters['format_currency'] = format_currency

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'app/static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/health')
def health():
    return jsonify(healthy=True)

@app.route('/')
def home():
    return redirect(url_for('get_tokens'))

# @app.route('/all')
# def top():
#     # Fetch and process data from the local database
#     data = plot.plot_ohlc_data()


#     # Generate a plot
#     img = io.BytesIO()
#     plt.figure()
#     data.plot(kind='bar')
#     plt.savefig(img, format='png')
#     img.seek(0)
#     plot_url = base64.b64encode(img.getvalue()).decode()

#     # Render the template with the plot
#     return render_template('plot.html', plot_url=plot_url)

@app.route('/tokens')
def get_tokens():
    search_query = request.args.get('query', '')

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'asc')
    offset = (page - 1) * per_page

    def datetime_friendly(dt):
        datetime_obj = datetime.strptime(dt, DB_TIME_FORMAT)

        return datetime_obj.strftime(READABLE_TIME_FORMAT)

    summary = db.query_db("""SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN ai_degen = 'green' THEN 1 ELSE 0 END) AS green,
        AVG(marketcap) AS average_marketcap
        FROM
        token_data""", {})

    if search_query:
        parameters = {'search_query': f"%{search_query}%"}
        if ENV == 'dev':
            query = f"SELECT * FROM token_data WHERE name LIKE :search_query"
        else:
            query = f"SELECT * FROM token_data WHERE name ILIKE %(search_query)s"
    else:
        parameters = {'limit': per_page, 'offset': offset}
        if ENV == 'dev':
            query = f"SELECT * FROM token_data order by {sort_by} {sort_order} LIMIT :limit OFFSET :offset"
        else:
            query = f"SELECT * FROM token_data order by {sort_by} {sort_order} LIMIT %(limit)s OFFSET %(offset)s"

    tokens = db.query_db(query, parameters)

    prev_page_url = url_for('get_tokens', page=page-1, query=search_query) if page > 1 else None
    next_page_url = url_for('get_tokens', page=page+1, query=search_query)

    return render_template('list_view.html',
                            tokens=tokens,
                            summary=summary[0],
                            sort_by=sort_by,
                            sort_order=sort_order,
                            datetime_friendly=datetime_friendly,
                            prev_page_url=prev_page_url,
                            next_page_url=next_page_url,
                            page=page
                            )

@app.route('/tokens/<token>')
def token_detail(token):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    bot_timestamp = int(datetime_to_epoch(date) - 18000*2)
    print("fetching plot data")
    pool_address = get_solana_pool_address(token)
    image = plot_ohlc_data(pool_address, bot_timestamp)
    if image is not None:
        # Encode the image bytes to base64
        image_base64 = base64.b64encode(image).decode('utf-8')
        return render_template('plot.html', token=token, image=image_base64)
    else:
        print("shit")
        return "Could not generate plot", 404

from flask import jsonify, Flask, redirect, request, url_for, render_template, send_file
import sqlite3
import os
from datetime import datetime
# from plot import datetime_to_epoch, get_solana_pool_address, plot_ohlc_data
from .db import DATABASE_CONFIG, DATABASE_TYPE, DatabaseController

app = Flask(__name__)

DEBUG=False

ENV = os.getenv('ENV')
db = DatabaseController(DATABASE_CONFIG[DATABASE_TYPE], DATABASE_TYPE)

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

# fuck, this is dumber than copy pasta
def makeDBString(s):
    sqlite = ENV == 'dev'
    if sqlite:
        return f":{s}"
    else:
        return f"%({s})s"

@app.route('/tokens')
def get_tokens():
    search_query = request.args.get('query', '')

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'asc')
    offset = (page - 1) * per_page

    def datetime_friendly(dt):
        datetime_obj = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')

        return datetime_obj.strftime('%b %d %H:%M')

    if search_query:
        parameters = {'search_query': '%' + search_query + '%'}
        if ENV == 'dev':
            query = f"SELECT * FROM token_data WHERE name LIKE :search_query"
        else:
            query = f"SELECT * FROM token_data WHERE name ILIKE '%(search_query)s%'"
    else:
        parameters = {'limit': per_page, 'offset': offset}
        if ENV == 'dev':
            query = f"SELECT * FROM token_data order by {sort_by} {sort_order} LIMIT :limit OFFSET :offset"
        else:
            query = f"SELECT * FROM token_data order by {sort_by} {sort_order} LIMIT %(limit)s OFFSET %(offset)s"

    tokens = db.query_db(query, parameters)

    return render_template('list_view.html', tokens=tokens, sort_by=sort_by, sort_order=sort_order, datetime_friendly=datetime_friendly)

# @app.route('/tokens/<token>')
# def token_detail(token):
#     date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     bot_timestamp = int(datetime_to_epoch(date) - 18000*2)
#     print("fetching plot data")
#     pool_address = get_solana_pool_address(token)
#     image = plot_ohlc_data(pool_address, bot_timestamp)
#     if image is not None:
#         # Encode the image bytes to base64
#         image_base64 = base64.b64encode(image).decode('utf-8')
#         return render_template('plot.html', token=token, image=image_base64)
#     else:
#         print("shit")
#         return "Could not generate plot", 404

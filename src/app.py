from flask import Flask, redirect, request, url_for, render_template, send_file
from flask_socketio import SocketIO
import sqlite3
import os
import pandas as pd
from datetime import datetime
import io
from .db import DATABASE_CONFIG, DATABASE_TYPE, DatabaseController
import base64


app = Flask(__name__)


DEBUG=False
socketio = SocketIO(app)

db = DatabaseController(DATABASE_CONFIG[DATABASE_TYPE], DATABASE_TYPE)

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
    per_page = request.args.get('per_page', 50, type=int)
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'asc')
    offset = (page - 1) * per_page

    if search_query:
        tokens = db.query_db(f"SELECT * FROM token_data WHERE name LIKE ? ORDER BY {sort_by} {sort_order}", ('%' + search_query + '%',))
    else:
        tokens =  db.query_db(f'SELECT * FROM token_data ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?', (per_page, offset))


    return render_template('list_view.html', tokens=tokens, sort_by=sort_by, sort_order=sort_order)

# @app.route('/tokens/<token>')
# def token_detail(token):
#     date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# 
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



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    socketio.run(app, host='0.0.0.0', port=port, debug=DEBUG)

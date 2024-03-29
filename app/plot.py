import requests
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.dates as mdates
matplotlib.use('Agg')  # Use the 'Agg' backend, which is non-interactive and does not require a GUI
from datetime import datetime
import time
import csv
import os
import numpy as np
import sqlite3

def fetch_ohlc_data(pool_address, bot_timestamp):
    time_diff_minutes = get_time_diff_minutes(bot_timestamp)
    interval, timeframe = get_interval_and_timeframe(time_diff_minutes)

    api_url = f"https://api.geckoterminal.com/api/v2/networks/solana/pools/{pool_address}/ohlcv/{timeframe}"
    headers = {"Accept": "application/json;version=20230302"}
    params = {
        "aggregate": interval,
        "currency": "usd",
        "limit": 1000,
    }

    response = requests.get(api_url, headers=headers, params=params)
    data = response.json()

    if "data" in data and "meta" in data:
        return data["data"], data["meta"]
    else:
        return None, None

def fetch_1m_data(pool_address, bot_timestamp):
    api_url = f"https://api.geckoterminal.com/api/v2/networks/solana/pools/{pool_address}/ohlcv/minute"
    headers = {"Accept": "application/json;version=20230302"}
    
    before_timestamp = int(bot_timestamp.timestamp()) + 300  # 5 minutes after bot signal time
    params = {
        "before_timestamp": before_timestamp,
        "limit": 10,  # Fetch 10 candlesticks (5 minutes before and 5 minutes after)
    }

    response = requests.get(api_url, headers=headers, params=params)
    data = response.json()

    if "data" in data and "meta" in data:
        return data["data"], data["meta"]
    else:
        return None, None

def get_time_diff_minutes(bot_timestamp):
    current_timestamp = int(time.time())
    time_diff = current_timestamp - bot_timestamp
    time_diff_minutes = time_diff // 60
    return time_diff_minutes

def get_interval_and_timeframe(time_diff_minutes):
    if time_diff_minutes <= 1000:
        interval = 1
        timeframe = "minute"
    elif time_diff_minutes <= 5000:
        interval = 5
        timeframe = "minute"
    elif time_diff_minutes <= 15000:
        interval = 15
        timeframe = "minute"
    elif time_diff_minutes <= 60000:
        interval = 1
        timeframe = "hour"
    elif time_diff_minutes <= 240000:
        interval = 4
        timeframe = "hour"
    elif time_diff_minutes <= 720000:
        interval = 12
        timeframe = "hour"
    else:
        interval = 1
        timeframe = "day"

    return interval, timeframe

def plot_candlesticks(ax, df, interval):
    if interval == 1:
        width = 0.0005
    elif interval == 5:
        width = 0.002
    elif interval == 15:
        width = 0.005
    elif interval == 60:
        width = 0.02
    elif interval == 240:
        width = 0.08
    elif interval == 720:
        width = 0.24
    else:
        width = 0.5

    up = df[df["close"] >= df["open"]]
    down = df[df["close"] < df["open"]]

    # Plot candle body
    ax.bar(up["timestamp"], up["close"] - up["open"], width, bottom=up["open"], color="green")
    ax.bar(down["timestamp"], down["close"] - down["open"], width, bottom=down["open"], color="red")

    # Plot wicks
    ax.vlines(up["timestamp"], up["low"], up["high"], color="green", linewidth=0.5)
    ax.vlines(down["timestamp"], down["low"], down["high"], color="red", linewidth=0.5)

def process_data(data):
    ohlcv_data = data
    df = pd.DataFrame(ohlcv_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

    return df

def plot_bot_call(ax, bot_timestamp, df, pool_address):
    star_size = 200
    star_color = 'magenta'
    border_color = 'black'
    border_width = 1

    # Fetch 1-minute candlestick data around the bot signal time
    data_1m, meta_1m = fetch_1m_data(pool_address, bot_timestamp)
    if data_1m:
        df_1m = process_data(data_1m["attributes"]["ohlcv_list"])
        closest_timestamp_1m = min(df_1m['timestamp'], key=lambda x: abs(x - bot_timestamp))
        candle_1m = df_1m[df_1m['timestamp'] == closest_timestamp_1m]

        if not candle_1m.empty:
            open_price_1m = candle_1m['open'].values[0]
            close_price_1m = candle_1m['close'].values[0]
            bot_price = close_price_1m
        else:
            bot_price = None
    else:
        bot_price = None

    if bot_price is not None:
        ax.scatter(
            bot_timestamp,
            bot_price,
            s=star_size,
            marker='*',
            color=star_color,
            edgecolors=border_color,
            linewidths=border_width,
            label=f'Seer Signal {bot_price:.5f}',
            zorder=3
        )

def configure_plot(ax, pool_address, meta, interval, timeframe, color=""):
    base_symbol = meta["base"]["symbol"]
    quote_symbol = meta["quote"]["symbol"]
    quote_str = quote_symbol.replace("$", "")
    interval_str = f"{interval}{timeframe[0]}"

    # Format x-axis tick labels to show hour and date
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:00"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45, ha='right')

    ax.set_xlabel("Time", color="white")
    ax.set_ylabel(f"Price (USD)", color="white")
    ax.set_title(f"{interval_str} price for {base_symbol}/{quote_str} pool", color="white")
    ax.legend()

    ax.grid(which="major", linestyle="-", linewidth=0.5, color="gray", alpha=0.3)
    ax.grid(which="minor", linestyle="--", linewidth=0.25, color="gray", alpha=0.2)
    ax.minorticks_on()

    handles, labels = ax.get_legend_handles_labels()
    new_handles = []
    for handle, label in zip(handles, labels):
        if label == "Seer Signal":
            new_handles.append(plt.Line2D([], [], marker='*', markersize=13, color='magenta', markeredgecolor='black', markeredgewidth=1, linestyle='None'))
        else:
            new_handles.append(handle)
    ax.legend(new_handles, labels)

    # Set dark background and text colors
    fig = ax.figure
    fig.set_facecolor("#121212")
    ax.set_facecolor("#121212")
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.yaxis.label.set_color('white')
    ax.xaxis.label.set_color('white')
    ax.title.set_color('white')
    ax.legend(facecolor='#121212', edgecolor='white', labelcolor='white')

    filename = f"{base_symbol}.png"
    return filename

def datetime_to_epoch(datetime_str):
    dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    epoch_time = int(dt.timestamp())
    return epoch_time

def get_solana_pool_address(token_address):
    api_url = f"https://api.geckoterminal.com/api/v2/networks/solana/tokens/{token_address}/pools?page=1"
    headers = {"Accept": "application/json"}

    response = requests.get(api_url, headers=headers)
    data = response.json()

    # If override is True, return the first pool's address, if available
    if "data" in data and data["data"]:
        pool = data["data"][0] #first pool
        return pool["attributes"]["address"]
    
    return None

def plot_ohlc_data(pool_address, bot_timestamp, color="unknown"):
    data, meta = fetch_ohlc_data(pool_address, bot_timestamp)
    shifted_data = data["attributes"]["ohlcv_list"]
    dt = 0
    for t in shifted_data:
        t[0] = t[0] - dt

    df = process_data(shifted_data)

    bot_timestamp = pd.to_datetime(bot_timestamp, unit="s")
    start_time = bot_timestamp - pd.Timedelta(minutes=120)
    filtered_df = df[df["timestamp"] >= start_time]
    if filtered_df.empty:
        filtered_df = df

    time_diff_minutes = get_time_diff_minutes(bot_timestamp.timestamp())
    interval, timeframe = get_interval_and_timeframe(time_diff_minutes)
    fig, ax = plt.subplots(figsize=(12, 6))
    plot_candlesticks(ax, filtered_df, interval)
    plot_bot_call(ax, bot_timestamp, filtered_df, pool_address)

    # Find the candle closest to the bot call timestamp
    closest_candle = filtered_df.iloc[np.argmin(np.abs(filtered_df['timestamp'] - bot_timestamp))]
    bot_call_price = closest_candle['close'] + 0.25*(closest_candle['high'] - closest_candle["close"])
    bot_call_time = closest_candle['timestamp']

    # Find the maximum closing price after the bot call
    after_bot_call_df = filtered_df[filtered_df['timestamp'] > bot_timestamp]
    if not after_bot_call_df.empty:
        max_close_price = after_bot_call_df['close'].max()
        max_close_time = after_bot_call_df.loc[after_bot_call_df['close'].idxmax(), 'timestamp']
        max_close_timestamp = after_bot_call_df.loc[after_bot_call_df['close'].idxmax(), 'timestamp']

        # Find the minimum closing price between the bot call and the maximum closing price
        min_low_price = after_bot_call_df.loc[after_bot_call_df['timestamp'] <= max_close_timestamp, 'low'].min()
        min_low_time = after_bot_call_df.loc[after_bot_call_df['low'] == min_low_price, 'timestamp'].iloc[0]

        # Calculate the percentage gain and loss
        max_gain_pct = max((max_close_price - bot_call_price) / bot_call_price * 100, 0)
        max_loss_pct = min((min_low_price - bot_call_price) / bot_call_price * 100, 0)

        # Plot the horizontal lines for maximum gain and loss
        ax.axhline(y=-100, color='green', linestyle='--', linewidth=1, label=f"Max Gain {max_close_price:.5f} ({max_gain_pct:.2f}%)")
        ax.axhline(y=-100, color='red', linestyle='--', linewidth=1, label=f"Max Loss {min_low_price:.5f} ({max_loss_pct:.2f}%)")
    else:
         max_close_price, max_close_time, min_low_price, min_low_time, max_gain_pct, max_loss_pct = [None] * 6
    
    configure_plot(ax, pool_address, meta, interval, timeframe, color)

    ymin = filtered_df["low"].min()
    ymax = filtered_df["close"].max()
    ax.set_ylim(ymin, ymax)

    plt.tight_layout()

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    plt.close(fig)
    output.seek(0)

    return output.getvalue(),

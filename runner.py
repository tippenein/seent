from telethon import TelegramClient
from telethon.tl.types import PeerChannel
import sqlite3
from datetime import datetime
import re
import time
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

# Retrieve the API ID, API HASH, and PHONE from environment variables
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')
channel_username = PeerChannel(2015897529)


async def fetch_messages(client, channel, limit=500, delay=1):
    messages = []
    offset_id = 0
    while len(messages) < limit:
        # Fetch a batch of messages
        batch = await client.get_messages(channel, limit=min(100, limit - len(messages)), offset_id=offset_id)
        messages.extend(batch)

        # Check if we have fetched all messages
        if len(batch) == 0:
            break

        # Update the offset_id to the ID of the last message in the batch
        offset_id = batch[-1].id

        # Sleep for the specified delay to avoid hitting rate limits
        await asyncio.sleep(delay)

    return messages

def degen_color(emoji):
    if emoji:
        # Convert the Unicode emoji to the color name
        if emoji == '🔴':
            return 'red'
        elif emoji == '🟡':
            return 'yellow'
        elif emoji == '🟢':
            return 'green'
        else:
            return 'unknown'  # Default case if the emoji is not recognized
    else:
        return None

def parse_token_data(raw_text):
    token_pattern = re.compile(r'Token: ([-\w.]+)')
    name_pattern = re.compile(r'Name: ([-\$\w./]+)')
    price_pattern = re.compile(r'Price: ([\d.]+)')
    marketcap_pattern = re.compile(r'Latest Marketcap: ([\d.]+[kmb]?)')
    volume_pattern = re.compile(r'Volume 24h: ([\d.]+[kmb]?)')
    memeability_pattern = re.compile(r'Memeability: ([\d.]+)')
    ai_degen_pattern = re.compile(r'AI Degen: (\S+)')
    top_holders_pattern = re.compile(r'Top 20 Holders: ([\d.]+)')
    total_holders_pattern = re.compile(r'Total Holders: (\d+)')
    transactions_pattern = re.compile(r'Transactions: (\d+)')
    price_change_pattern = re.compile(r'PriceChange 5min: ([\d.]+)')
    data = {}
    marketcap_match = marketcap_pattern.search(raw_text)
    data['marketcap'] = marketcap_match.group(1) if marketcap_match else None

    memeability_match = memeability_pattern.search(raw_text)
    data['memeability'] = memeability_match.group(1) if memeability_match else None

    volume_24h_match = volume_pattern.search(raw_text)
    data['volume_24h'] = volume_24h_match.group(1) if volume_24h_match else None

    ai_degen_match = ai_degen_pattern.search(raw_text)
    data['ai_degen'] = degen_color(ai_degen_match.group(1)) if ai_degen_match else None
    # Search for matches in the raw text
    token_match = token_pattern.search(raw_text)
    data['token'] = token_match.group(1) if token_match else None

    name_match = name_pattern.search(raw_text)
    data['name'] = name_match.group(1) if name_match else None

    price_match = price_pattern.search(raw_text)
    data['price'] = float(price_match.group(1)) if price_match else None

    top_20_holders_match = top_holders_pattern.search(raw_text)
    data['top_20_holders'] = float(top_20_holders_match.group(1)) if top_20_holders_match else 0.0

    total_holders_match = total_holders_pattern.search(raw_text)
    data['total_holders'] = int(total_holders_match.group(1)) if total_holders_match else 0

    transactions_match = transactions_pattern.search(raw_text)
    data['transactions'] = int(transactions_match.group(1)) if transactions_match else 0

    price_change_5min_match = price_change_pattern.search(raw_text)
    data['price_change_5min'] = float(price_change_5min_match.group(1)) if price_change_5min_match else 0.0


    return data

# Create the client and connect
client = TelegramClient('session_name', api_id, api_hash)

def setup_db(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS token_data (
            id INTEGER PRIMARY KEY,
            date TEXT,
            token TEXT,
            name TEXT,
            price REAL,
            marketcap TEXT,
            memeability REAL,
            volume_24h TEXT,
            ai_degen TEXT,
            top_20_holders REAL,
            total_holders INTEGER,
            transactions INTEGER,
            price_change_5min REAL
        )
        ''')
    cursor.close()


def insert(conn, data, date, id):
    # Convert the datetime object to a string in the SQLite datetime format

    # Start a transaction
    cursor = conn.cursor()
    try:
        # Check if the ID already exists
        cursor.execute('SELECT 1 FROM token_data WHERE id = ?', (id,))
        exists = cursor.fetchone()

        # If the ID does not exist, insert the new data
        if not exists:
            cursor.execute('''
            INSERT INTO token_data (
                id, date, token, name, price, marketcap, memeability, volume_24h, ai_degen, top_20_holders,
                total_holders, transactions, price_change_5min
            ) VALUES (
                :id, :date, :token, :name, :price, :marketcap, :memeability, :volume_24h, :ai_degen, :top_20_holders,
                :total_holders, :transactions, :price_change_5min
            )
            ''', {'id': id, 'date': date, **data})

            # Commit the changes if the insert was successful
            conn.commit()
            return 1
        else:
            print(f"Entry with ID {id} already exists. Skipping insert.")
            return 0
    except sqlite3.Error as e:
        # If an error occurs, rollback the transaction
        conn.rollback()
        print(f"An error occurred: {e}")
        return 0
    finally:
        # Close the cursor
        cursor.close()

async def main():
    conn = sqlite3.connect('seent.db')
    setup_db(conn)
    # Connect to the client
    await client.start()
    print("Client Created")

    # Ensure you're authorized
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except:
            await client.sign_in(password=input('Password: '))

    # Access the channel
    channel = await client.get_entity(channel_username)

    # arbitrary limit of 1000
    messages = await fetch_messages(client, channel, limit=100, delay=1)

    count = 0
    for message in messages:
        id = message.id
        date = message.date
        date_str = date.strftime('%Y-%m-%d %H:%M:%S')
        token_data = parse_token_data(message.message) if message.message else None
        if token_data:
            count += insert(conn, token_data, date_str, id)
        else:
            print(f"An error occurred for message {id} at {date_str}")

    print(f"Added {count} new calls")
    conn.close()

with client:
    client.loop.run_until_complete(main())

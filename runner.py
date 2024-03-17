from telethon import TelegramClient
from telethon.tl.types import PeerChannel
import sqlite3
from datetime import datetime
import re
import time
import asyncio
from dotenv import load_dotenv
from seer_parser import parse_token_data
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
            marketcap REAL,
            memeability REAL,
            volume_24h REAL,
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
                :id, :date, :token, :name, :price, :marketcap, :memeability, :volume, :ai_degen, :top_20_holders,
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
    messages = await fetch_messages(client, channel, limit=150, delay=1)

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

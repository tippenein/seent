from telethon import TelegramClient
from telethon.tl.types import InputPeerChannel
import sqlite3
from datetime import datetime
import re
import time
import asyncio
from dotenv import load_dotenv
from seer_parser import parse_token_data
import os

# current seer version handled
CURRENT_VERSION='v1.35'

load_dotenv()

# Retrieve the API ID, API HASH, and PHONE from environment variables
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')
megagroup_id = os.getenv('MEGAGROUP_ID')
megagroup_access_hash = os.getenv('MEGAGROUP_ACCESS_HASH')
# https://web.telegram.org/a/#-1002037088573_20
parent_message_id = 20


async def fetch_messages(client, limit=500, delay=1):
    messages = []
    offset_id = 0
    megagroup_entity = InputPeerChannel(channel_id=int(megagroup_id), access_hash=int(megagroup_access_hash))

    while len(messages) < limit:
        # Fetch a batch of messages
        batch = await client.get_messages(
                megagroup_entity,
                limit=min(100, limit - len(messages)),
                offset_id=offset_id,
                reply_to=parent_message_id
            )
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
            liquidity REAL,
            memeability REAL,
            name_originality REAL,
            description_originality REAL,
            volume integer,
            ai_degen TEXT,
            ai_degen_death REAL,
            ai_degen_red REAL,
            ai_degen_yellow REAL,
            ai_degen_green REAL,
            top_20_holders REAL,
            total_holders INTEGER,
            transactions INTEGER,
            price_change_5min REAL
        )
        ''')
    cursor.close()


def insert(conn, data, date, id):
    cursor = conn.cursor()
    try:
        # Check if the ID already exists
        cursor.execute('SELECT 1 FROM token_data WHERE id = ?', (id,))
        exists = cursor.fetchone()

        # If the ID does not exist, insert the new data
        if not exists:
            cursor.execute('''
            INSERT INTO token_data (
                id, date, token, name, price, marketcap, liquidity, memeability, name_originality,
                description_originality, volume, ai_degen, ai_degen_death, ai_degen_green,
                ai_degen_red, ai_degen_yellow, top_20_holders, total_holders, transactions, price_change_5min
            ) VALUES (
                :id, :date, :token, :name, :price, :marketcap, :liquidity, :memeability, :name_originality,
                :description_originality, :volume, :ai_degen, :ai_degen_death, :ai_degen_green, :ai_degen_red,
                :ai_degen_yellow, :top_20_holders, :total_holders, :transactions, :price_change_5min
            )
            ''', {'id': id, 'date': date, **data})

            conn.commit()
            return 1
        else:
            print(f"Entry with ID {id} already exists. Skipping insert.")
            return 0
    except sqlite3.Error as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        return 0
    finally:
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

    # arbitrary limit
    messages = await fetch_messages(client, limit=70, delay=1)

    count = 0
    for message in messages:
        id = message.id + 5000 # offset because the old version ids overlap
        date = message.date
        date_str = date.strftime('%Y-%m-%d %H:%M:%S')
        token_data = parse_token_data(message.message) if message.message else None
        # if token_data['version'] != CURRENT_VERSION:
        #     print("Warning: parser version out of date")

        if token_data is not None:
            count += insert(conn, token_data, date_str, id)
        else:
            print(f"An error occurred for message {id} at {date_str}")

    print(f"Added {count} new calls")
    conn.close()

with client:
    client.loop.run_until_complete(main())


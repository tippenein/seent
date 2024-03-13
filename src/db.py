import os
from dotenv import load_dotenv
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

VERCEL_ENV = os.getenv('VERCEL_ENV')
POSTGRES_DBNAME = os.getenv('POSTGRES_DBNAME')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')

DATABASE_CONFIG = {
    'sqlite': {
        'DATABASE': './seent.db',
    },
    'postgres': {
        'DATABASE': POSTGRES_DBNAME,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': POSTGRES_HOST,
        'PORT': '5432',
    }
}

# Choose the database type here ('sqlite' or 'postgres')
def get_database_type():
  if VERCEL_ENV == 'dev':
    return 'sqlite'
  else:
    return 'postgres'

class DatabaseController:
    def __init__(self, config, db_type):
        self.config = config
        self.db_type = db_type

    def get_connection(self):
        if self.db_type == 'sqlite':
            conn = sqlite3.connect(self.config['DATABASE'])
            conn.row_factory = sqlite3.Row
            return conn
        elif self.db_type == 'postgres':
            print(self.config)
            conn = psycopg2.connect(
                dbname=self.config['DATABASE'],
                user=self.config['USER'],
                password=self.config['PASSWORD'],
                host=self.config['HOST'],
                port=self.config['PORT']
            )
            return conn
        else:
            raise ValueError("Unsupported database type")

    def query_db(self, query, args=(), one=False):
        conn = self.get_connection()
        if self.db_type == 'postgres':
            cur = conn.cursor(cursor_factory=RealDictCursor)
        else:
            # For SQLite and other databases, do not use cursor_factory
            cur = conn.cursor()
        cur.execute(query, args)
        rv = cur.fetchall()
        cur.close()
        conn.close()
        return (rv[0] if rv else None) if one else rv

DATABASE_TYPE = get_database_type()

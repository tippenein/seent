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
    return 'postgres'
#   if VERCEL_ENV == 'dev':
#     return 'sqlite'
#   else:
#     return 'postgres'

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

    def query_db(self, query, parameters):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if self.db_type == 'sqlite':
                cursor.execute(query, parameters)
            elif self.db_type == 'postgres':
                query = cursor.mogrify(query, parameters).decode('utf-8')
                cursor.execute(query)
            else:
                raise ValueError("Unsupported database type")
            columns = [col[0] for col in cursor.description]

        # Fetch all rows as a list of dictionaries
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return rows
        except (sqlite3.Error, psycopg2.Error) as e:
            print("Database Error:", e)
        finally:
            cursor.close()
            conn.close()

DATABASE_TYPE = get_database_type()

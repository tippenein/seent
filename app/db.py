import os
from dotenv import load_dotenv
import sqlite3
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor

load_dotenv()

ENV = os.getenv('ENV')
POSTGRES_DBNAME = os.getenv('POSTGRES_DBNAME')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')

DATABASE_CONFIG = {
    'sqlite': {
        'DATABASE': './seent.db',
    },
    'postgres': {
        'DATABASE': POSTGRES_DBNAME,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': POSTGRES_HOST,
        'PORT': POSTGRES_PORT,
    }
}

# Choose the database type here ('sqlite' or 'postgres')
def get_database_type():
  print(ENV)
  if ENV == 'dev':
    print("using sqlite")
    return 'sqlite'
  else:
    print("using postgres")
    return 'postgres'

class DatabaseController:
    def __init__(self, config, db_type):
        self.config = config
        self.db_type = db_type
        self.pool = ThreadedConnectionPool(10, 15,
                dbname=config['DATABASE'],
                user=config['USER'],
                password=config['PASSWORD'],
                host=config['HOST'],
                port=config['PORT']) if self.db_type == 'postgres' else None

    def get_connection(self):
        if self.db_type == 'sqlite':
            conn = sqlite3.connect(self.config['DATABASE'])
            conn.row_factory = sqlite3.Row
            return conn
        elif self.db_type == 'postgres':
            return self.pool.getconn()
            #     dbname=self.config['DATABASE'],
            #     user=self.config['USER'],
            #     password=self.config['PASSWORD'],
            #     host=self.config['HOST'],
            #     port=self.config['PORT']
            # )
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
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except (sqlite3.Error, psycopg2.Error) as e:
            print("Database Error:", e)
        finally:
            cursor.close()
            if self.db_type == 'postgres':
                self.pool.putconn(conn)
            else:
                conn.close()

DATABASE_TYPE = get_database_type()

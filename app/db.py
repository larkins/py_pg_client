import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config

class Database:
    def __init__(self):
        self.connection = None
    
    def get_connection(self):
        if self.connection is None or self.connection.closed:
            self.connection = psycopg2.connect(Config.DATABASE_URL)
        return self.connection
    
    def close(self):
        if self.connection and not self.connection.closed:
            self.connection.close()
            self.connection = None
    
    def execute(self, query, params=None, fetch=False):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(query, params)
            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = None
            return result
        finally:
            cursor.close()
    
    def execute_one(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(query, params)
            conn.commit()
            result = cursor.fetchone()
            return result
        finally:
            cursor.close()

def init_db():
    """Initialize database tables"""
    db = Database()
    
    # Domain whitelist table
    db.execute("""
        CREATE TABLE IF NOT EXISTS domain_whitelist (
            id SERIAL PRIMARY KEY,
            domain VARCHAR(255) UNIQUE NOT NULL,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # User preferences table
    db.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            id SERIAL PRIMARY KEY,
            user_email VARCHAR(255) NOT NULL,
            setting_name VARCHAR(100) NOT NULL,
            setting_value TEXT,
            UNIQUE(user_email, setting_name)
        )
    """)
    
    db.close()
    print("Database initialized successfully")

def get_db():
    """Get database instance"""
    return Database()

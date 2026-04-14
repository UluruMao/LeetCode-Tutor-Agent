import sqlite3
from datetime import datetime

DB_NAME = "leetcode_history.db"

def init_db():
    """Creates the SQLite database and the table if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create a table with columns for analytics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS failures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            problem_title TEXT,
            tags TEXT,
            error_type TEXT,
            ai_advice TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_failure_to_db(title, tags, error_type, advice):
    """Inserts a new failed submission into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO failures (timestamp, problem_title, tags, error_type, ai_advice)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, title, tags, error_type, advice))
    
    conn.commit()
    conn.close()

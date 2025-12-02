"""
Database Helper for New CRM Modules
Provides a simple get_db function for blueprints
"""

import sqlite3
import os

# Get absolute path to database
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crm_database.db')

def get_db(db_path=None):
    """Get database connection with row factory"""
    if db_path is None:
        db_path = DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# database.py
import sqlite3
import json
from config import DB_PATH

class DatabaseManager:
    def __init__(self):
        # Establish connection to SQLite
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        # Create a table to store the nodes and links of each Mind Map
        query = """
        CREATE TABLE IF NOT EXISTS mind_maps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            graph_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def save_map(self, title, nodes, links):
        # Serialize graph data to JSON string for storage
        data = json.dumps({"nodes": nodes, "links": links})
        query = "INSERT INTO mind_maps (title, graph_data) VALUES (?, ?)"
        cursor = self.conn.cursor()
        cursor.execute(query, (title, data))
        self.conn.commit()
        return cursor.lastrowid

    def get_all_maps(self):
        # Retrieve all saved maps for the UI list
        query = "SELECT id, title, created_at FROM mind_maps ORDER BY created_at DESC"
        cursor = self.conn.execute(query)
        return cursor.fetchall()
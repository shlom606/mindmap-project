import sqlite3
import json

class MindMapStorage:
    def __init__(self, db_path="mindmap_system_6.db"):
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """Initializes the multi-user schema."""
        with self._get_connection() as conn:
            # Table for Users
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL
                )
            """)
            # Table for Mind Map metadata
            conn.execute("""
                CREATE TABLE IF NOT EXISTS maps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            # Table for graph structure (Nodes/Edges stored as JSON for flexibility)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS map_data (
                    map_id INTEGER PRIMARY KEY,
                    graph_json TEXT NOT NULL,
                    FOREIGN KEY (map_id) REFERENCES maps (id)
                )
            """)

    def save_user_map(self, username, map_title, graph_data):
        """
        Saves a generated mind map for a specific user.
        graph_data should be the output from GraphBuilder.create_structure.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Ensure user exists
            cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_id = cursor.fetchone()['id']

            # 2. Create Map entry
            cursor.execute("INSERT INTO maps (user_id, title) VALUES (?, ?)", (user_id, map_title))
            map_id = cursor.lastrowid

            # 3. Save serialized graph data (D3.js format)
            cursor.execute("INSERT INTO map_data (map_id, graph_json) VALUES (?, ?)", 
                           (map_id, json.dumps(graph_data)))
            conn.commit()
            return map_id

    def load_user_maps(self, username):
        """Retrieves all mind maps created by a user."""
        query = """
            SELECT m.id, m.title, m.created_at, md.graph_json 
            FROM maps m
            JOIN users u ON m.user_id = u.id
            JOIN map_data md ON m.id = md.map_id
            WHERE u.username = ?
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (username,))
            return [dict(row) for row in cursor.fetchall()]
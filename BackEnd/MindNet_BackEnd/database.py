import sqlite3
import json
import bcrypt

class MindMapStorage:
    def __init__(self, db_path="mindmap_system_6.db"):
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """Initializes the schema and ensures changes are saved."""
        with self._get_connection() as conn:
            # Use a cursor to execute multiple commands
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS map_data (
                    map_id INTEGER PRIMARY KEY,
                    graph_json TEXT NOT NULL,
                    FOREIGN KEY (map_id) REFERENCES maps (id)
                )
            """)
            # Committing is usually automatic in a 'with' block, 
            # but adding it explicitly ensures the tables are written.
            conn.commit()
    def signup_user(self, username, password):
            # 1. Truncate and encode to bytes
            safe_password = password[:72].encode('utf-8')
            
            # 2. Generate salt and hash
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(safe_password, salt)
            
            try:
                with self._get_connection() as conn:
                    # Store the hash as a string in the DB
                    conn.execute(
                        "INSERT INTO users (username, password) VALUES (?, ?)", 
                        (username, hashed_pw.decode('utf-8'))
                    )
                    conn.commit()
                    return True
            except sqlite3.IntegrityError:
                return False

    def authenticate_user(self, username, password):
        safe_password = password[:72].encode('utf-8')
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            
            if row:
                # 3. Retrieve stored hash and check it
                stored_hash = row['password'].encode('utf-8')
                if bcrypt.checkpw(safe_password, stored_hash):
                    return True
            return False
    def save_user_map(self, username, map_title, graph_data):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Look up the user
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            
            # 2. Safety Check: If user isn't found, handle it gracefully
            if row is None:
                print(f"Error: User '{username}' not found in database.")
                # Option A: Raise an error
                raise ValueError(f"User {username} does not exist. Please log in again.")
                # Option B: Or auto-create the user if you prefer (less secure)
            
            user_id = row['id']

            # 3. Create Map entry
            cursor.execute("INSERT INTO maps (user_id, title) VALUES (?, ?)", (user_id, map_title))
            map_id = cursor.lastrowid

            # 4. Save serialized graph data
            cursor.execute("INSERT INTO map_data (map_id, graph_json) VALUES (?, ?)", 
                        (map_id, json.dumps(graph_data)))
            conn.commit()
            return map_id

    def load_user_maps(self, username):
        """FIX: This method was missing in your error message"""
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

    def delete_user_map(self, username, map_id):
        """Deletes a map only if it belongs to the authenticated user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Security: Join with users table to ensure the map belongs to the requester
            cursor.execute("""
                DELETE FROM maps 
                WHERE id = ? AND user_id = (SELECT id FROM users WHERE username = ?)
            """, (map_id, username))
            
            # Also clean up the heavy JSON data
            cursor.execute("DELETE FROM map_data WHERE map_id = ?", (map_id,))
            
            conn.commit()
            return cursor.rowcount > 0 # Returns True if a row was actually deleted
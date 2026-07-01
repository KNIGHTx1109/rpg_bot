import sqlite3
import json

DB_PATH = "rpg_state.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create player_state table
    c.execute('''
        CREATE TABLE IF NOT EXISTS player_state (
            id INTEGER PRIMARY KEY,
            health INTEGER,
            location TEXT,
            inventory TEXT
        )
    ''')
    # Create chat_history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )
    ''')
    
    # Initialize default state if not exists
    c.execute("SELECT COUNT(*) FROM player_state")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO player_state (id, health, location, inventory) VALUES (1, 100, 'Tavern', '[]')")
    
    conn.commit()
    conn.close()

def get_player_state():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT health, location, inventory FROM player_state WHERE id = 1")
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "health": row[0],
            "location": row[1],
            "inventory": json.loads(row[2])
        }
    return None

def update_player_state(health: int, location: str, inventory: list):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE player_state 
        SET health = ?, location = ?, inventory = ? 
        WHERE id = 1
    ''', (health, location, json.dumps(inventory)))
    conn.commit()
    conn.close()

def get_chat_history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]

def add_chat_message(role: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def reset_game():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM chat_history")
    c.execute("UPDATE player_state SET health = 100, location = 'Tavern', inventory = '[]' WHERE id = 1")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")

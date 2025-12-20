import sqlite3
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self, db_path="game.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # 1. The Catalog (The "Shop List")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards_catalog (
                card_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                rarity TEXT,
                image_url TEXT,
                description TEXT
            )
        """)
        
        # 2. The Inventory (The "Player's Backpack")
        # We store card_id here instead of the full name/url to save space
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                user_id TEXT,
                card_id INTEGER,
                timestamp TEXT,
                FOREIGN KEY(card_id) REFERENCES cards_catalog(card_id)
            )
        """)

        # Table for users info
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                balance INTEGER,
                daily_free INTEGER
            )
        """)
        self.conn.commit()

    # --- INVENTORY LOGIC ---
    def manage_balance(self, user_id, mode, amount):
        """Use this to manage a user's balance"""

        if mode == "add":
            self.cursor.execute("""
                UPDATE users
                SET balance = balance + ?
                WHERE user_id = ?;
            """, (amount, user_id))

        elif mode == "sub":
            self.cursor.execute("""
                UPDATE users
                SET balance = balance - ?
                WHERE user_id = ?;
            """, (amount, user_id))
        else:
            raise ValueError("Invalid mode. Use 'add' or 'sub'.")

        self.conn.commit()

    def check_balance(self, user_id):
        """Return user's current balance"""

        self.cursor.execute("""
            SELECT balance
            FROM users
            WHERE user_id = ?;
        """, (user_id,))

        row = self.cursor.fetchone()

        if row is None:
            return 0   # user not found → balance = 0

        return row[0]


    def add_card_to_catalog(self, name, rarity, url, desc):
        """Use this to register new cards into your game."""
        self.cursor.execute(
            "INSERT INTO cards_catalog (name, rarity, image_url, description) VALUES (?, ?, ?, ?)",
            (name, rarity, url, desc)
        )
        self.conn.commit()

    def add_to_inventory(self, user_id, card_id):
        """Saves a pulled card to the player's account."""
        now = datetime.now().isoformat()
        self.cursor.execute(
            "INSERT INTO inventory (user_id, card_id, timestamp) VALUES (?, ?, ?)",
            (str(user_id), card_id, now)
        )
        self.conn.commit()

    def get_user_inventory(self, user_id):
        """Returns all cards owned by a user with their full details."""
        query = """
            SELECT c.name, c.rarity, c.image_url 
            FROM inventory i
            JOIN cards_catalog c ON i.card_id = c.card_id
            WHERE i.user_id = ?
        """
        self.cursor.execute(query, (str(user_id),))
        return self.cursor.fetchall()

    def get_random_card_by_rarity(self, rarity):
        """Picks a random card from the catalog based on the rarity rolled."""
        self.cursor.execute("SELECT * FROM cards_catalog WHERE rarity = ? ORDER BY RANDOM() LIMIT 1", (rarity,))
        return self.cursor.fetchone()
    
        # --- COOLDOWN LOGIC ---

    def check_and_update_cooldown(self, user_id):
        user_id = str(user_id)
        now = datetime.now()
        one_day_ago = (now - timedelta(hours=24)).isoformat()

        # 1. Count how many cards this user got in the last 24 hours
        self.cursor.execute("""
            SELECT COUNT(*) FROM inventory 
            WHERE user_id = ? AND timestamp > ?
        """, (user_id, one_day_ago))
        
        pull_count = self.cursor.fetchone()[0]

        if pull_count >= 5:
            # 2. If they already pulled twice, find when the OLDEST of those 2 pulls happened
            # to tell them when they get a "charge" back.
            self.cursor.execute("""
                SELECT timestamp FROM inventory 
                WHERE user_id = ? AND timestamp > ?
                ORDER BY timestamp ASC LIMIT 1
            """, (user_id, one_day_ago))
            
            oldest_pull_str = self.cursor.fetchone()[0]
            oldest_pull_time = datetime.fromisoformat(oldest_pull_str)
            time_remaining = (oldest_pull_time + timedelta(hours=24)) - now
            
            return False, time_remaining

        # If count is 0 or 1, they are allowed to pull
        return True, None
    def get_card_by_name(self, user_id, card_name):
        """
        Returns a card owned by the user with the given card name.
        If the user owns multiple copies, returns one of them.
        """
        query = """
            SELECT 
                c.card_id,
                c.name,
                c.rarity,
                c.image_url,
                c.description
            FROM inventory i
            JOIN cards_catalog c ON i.card_id = c.card_id
            WHERE i.user_id = ?
            AND c.name = ?
            ORDER BY i.timestamp ASC
            LIMIT 1
        """
        self.cursor.execute(query, (str(user_id), card_name))
        row = self.cursor.fetchone()

        if not row:
            return None

        return {
            "card_id": row[0],
            "name": row[1],
            "rank": row[2],
            "image_url": row[3],
            "description": row[4],
        }
   

    def close(self):
        self.conn.close()
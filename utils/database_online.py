import os
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # 1. The Catalog (The "Shop List")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards_catalog (
                card_id SERIAL PRIMARY KEY,
                name TEXT,
                rarity TEXT,
                image_url TEXT,
                description TEXT
            );
        """)

        # 2. The Inventory (The "Player's Backpack")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                user_id TEXT,
                card_id INTEGER REFERENCES cards_catalog(card_id),
                timestamp TIMESTAMP
            );
        """)

        # 3. Cooldowns
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cooldowns (
                user_id TEXT PRIMARY KEY,
                last_pull TIMESTAMP
            );
        """)
        self.conn.commit()

    # --- INVENTORY LOGIC ---

    def add_card_to_catalog(self, name, rarity, url, desc):
        self.cursor.execute("""
            INSERT INTO cards_catalog (name, rarity, image_url, description)
            VALUES (%s, %s, %s, %s);
        """, (name, rarity, url, desc))
        self.conn.commit()

    def add_to_inventory(self, user_id, card_id):
        now = datetime.utcnow()
        self.cursor.execute("""
            INSERT INTO inventory (user_id, card_id, timestamp)
            VALUES (%s, %s, %s);
        """, (str(user_id), card_id, now))
        self.conn.commit()

    def get_user_inventory(self, user_id):
        query = """
            SELECT c.name, c.rarity, c.image_url
            FROM inventory i
            JOIN cards_catalog c ON i.card_id = c.card_id
            WHERE i.user_id = %s;
        """
        self.cursor.execute(query, (str(user_id),))
        return self.cursor.fetchall()

    def get_random_card_by_rarity(self, rarity):
        self.cursor.execute("""
            SELECT card_id, name, rarity, image_url, description
            FROM cards_catalog
            WHERE rarity = %s
            ORDER BY RANDOM()
            LIMIT 1;
        """, (rarity,))
        return self.cursor.fetchone()

    # --- COOLDOWN LOGIC ---

    def check_and_update_cooldown(self, user_id):
        user_id = str(user_id)
    
        # 計算 24 小時內抽卡次數
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM inventory
            WHERE user_id = %s
              AND timestamp > NOW() - INTERVAL '24 hours';
        """, (user_id,))
    
        pull_count = self.cursor.fetchone()[0]
    
        if pull_count >= 5:
            self.cursor.execute("""
                SELECT timestamp
                FROM inventory
                WHERE user_id = %s
                  AND timestamp > NOW() - INTERVAL '24 hours'
                ORDER BY timestamp ASC
                LIMIT 1;
            """, (user_id,))
    
            oldest_pull_time = self.cursor.fetchone()[0]
    
            # PostgreSQL 回來的是 datetime（aware）
            time_remaining = (oldest_pull_time + timedelta(hours=24)) - datetime.now(oldest_pull_time.tzinfo)
    
            return False, time_remaining
    
        return True, None


    def get_card_by_name(self, user_id, card_name):
        query = """
            SELECT
                c.card_id,
                c.name,
                c.rarity,
                c.image_url,
                c.description
            FROM inventory i
            JOIN cards_catalog c ON i.card_id = c.card_id
            WHERE i.user_id = %s
              AND c.name = %s
            ORDER BY i.timestamp ASC
            LIMIT 1;
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
        self.cursor.close()
        self.conn.close()

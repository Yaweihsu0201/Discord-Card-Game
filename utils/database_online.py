import os
import psycopg2
from datetime import datetime, timedelta, timezone, date
from dotenv import load_dotenv
load_dotenv()

class DatabaseManager:
    def __init__(self):

        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        self.cursor = self.conn.cursor()
        self.create_tables()

    # =========================
    # TABLE CREATION
    # =========================
    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards_catalog (
                card_id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                rarity TEXT NOT NULL,
                image_url TEXT,
                description TEXT
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                user_id TEXT NOT NULL,
                card_id INTEGER REFERENCES cards_catalog(card_id),
                timestamp TIMESTAMP NOT NULL
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                balance INTEGER NOT NULL DEFAULT 0,
                daily_remaining INTEGER NOT NULL DEFAULT 5,
                last_daily_reset DATE
            );
        """)

        self.conn.commit()

    # =========================
    # USER / BALANCE LOGIC
    # =========================
    def ensure_user(self, user_id):
        self.cursor.execute("""
            INSERT INTO users (user_id, balance, daily_remaining, last_daily_reset)
            VALUES (%s, 0, 5, CURRENT_DATE)
            ON CONFLICT (user_id) DO NOTHING;
        """, (str(user_id),))
        self.conn.commit()

    def manage_balance(self, user_id, mode, amount):
        self.ensure_user(user_id)

        if mode == "add":
            self.cursor.execute("""
                UPDATE users
                SET balance = balance + %s
                WHERE user_id = %s;
            """, (amount, str(user_id)))

        elif mode == "sub":
            self.cursor.execute("""
                UPDATE users
                SET balance = balance - %s
                WHERE user_id = %s;
            """, (amount, str(user_id)))

        else:
            raise ValueError("Invalid mode: use 'add' or 'sub'")

        self.conn.commit()

    def check_balance(self, user_id):
        self.ensure_user(user_id)
        self.cursor.execute("""
            SELECT balance FROM users WHERE user_id = %s;
        """, (str(user_id),))
        return self.cursor.fetchone()[0]

    # =========================
    # DAILY LIMIT LOGIC
    # =========================
    def reset_daily_if_needed(self, user_id):
        self.cursor.execute("""
            SELECT last_daily_reset FROM users WHERE user_id = %s;
        """, (str(user_id),))

        last_reset = self.cursor.fetchone()[0]
        today = date.today()

        if last_reset != today:
            self.cursor.execute("""
                UPDATE users
                SET daily_remaining = 5,
                    last_daily_reset = %s
                WHERE user_id = %s;
            """, (today, str(user_id)))
            self.conn.commit()

    def get_daily_remaining(self, user_id):
        self.ensure_user(user_id)
        self.reset_daily_if_needed(user_id)

        self.cursor.execute("""
            SELECT daily_remaining FROM users WHERE user_id = %s;
        """, (str(user_id),))

        return self.cursor.fetchone()[0]

    def consume_daily_pull(self, user_id):
        self.reset_daily_if_needed(user_id)

        self.cursor.execute("""
            UPDATE users
            SET daily_remaining = daily_remaining - 1
            WHERE user_id = %s AND daily_remaining > 0;
        """, (str(user_id),))

        self.conn.commit()
        return self.cursor.rowcount > 0

    # =========================
    # CARD CATALOG
    # =========================
    def add_card_to_catalog(self, name, rarity, image_url, description):
        self.cursor.execute("""
            INSERT INTO cards_catalog (name, rarity, image_url, description)
            VALUES (%s, %s, %s, %s);
        """, (name, rarity, image_url, description))
        self.conn.commit()

    def get_random_card_by_rarity(self, rarity):
        self.cursor.execute("""
            SELECT * FROM cards_catalog
            WHERE rarity = %s
            ORDER BY RANDOM()
            LIMIT 1;
        """, (rarity,))
        return self.cursor.fetchone()

    # =========================
    # INVENTORY
    # =========================
    def add_to_inventory(self, user_id, card_id):
        self.cursor.execute("""
            INSERT INTO inventory (user_id, card_id, timestamp)
            VALUES (%s, %s, %s);
        """, (str(user_id), card_id, datetime.utcnow()))
        self.conn.commit()

    def get_user_inventory(self, user_id):
        self.cursor.execute("""
            SELECT
                i.card_id,
                c.name,
                c.rarity,
                c.image_url
            FROM inventory i
            JOIN cards_catalog c ON i.card_id = c.card_id
            WHERE i.user_id = %s;
        """, (str(user_id),))
        return self.cursor.fetchall()

    def remove_from_inventory_by_card_id(self, user_id, card_id):
        """
        Remove ONE copy (oldest) of a card from inventory
        """
        self.cursor.execute("""
            DELETE FROM inventory
            WHERE ctid = (
                SELECT ctid
                FROM inventory
                WHERE user_id = %s AND card_id = %s
                ORDER BY timestamp ASC
                LIMIT 1
            );
        """, (str(user_id), card_id))

        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_card_by_card_id(self, user_id, card_id):
        self.cursor.execute("""
            SELECT
                c.card_id,
                c.name,
                c.rarity,
                c.image_url,
                c.description
            FROM inventory i
            JOIN cards_catalog c ON i.card_id = c.card_id
            WHERE i.user_id = %s
              AND i.card_id = %s
            ORDER BY i.timestamp ASC
            LIMIT 1;
        """, (str(user_id), card_id))

        row = self.cursor.fetchone()
        if not row:
            return None

        return {
            "card_id": row[0],
            "name": row[1],
            "ransk": row[2],
            "image_url": row[3],
            "description": row[4],
        }

    # =========================
    # CLEANUP
    # =========================
    def close(self):
        self.cursor.close()
        self.conn.close()
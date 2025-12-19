import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime 

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def main():
    print("Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    print("Connected ✅\n")

    # 1. CREATE TABLE
    print("Creating table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bot_test (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP
        );
    """)
    conn.commit()
    print("Table ready ✅\n")

    # 2. INSERT DATA
    print("Inserting data...")
    cur.execute("""
        INSERT INTO bot_test (user_id, message, created_at)
        VALUES (%s, %s, %s)
        RETURNING id;
    """, ("123456789", "Hello from bot test", datetime.utcnow()))
    inserted_id = cur.fetchone()[0]
    conn.commit()
    print(f"Inserted row with id = {inserted_id} ✅\n")

    # 3. FETCH DATA (THIS IS WHAT YOUR BOT DOES)
    print("Fetching data...")
    cur.execute("SELECT id, user_id, message, created_at FROM bot_test;")
    rows = cur.fetchall()

    for row in rows:
        print(row)

    print("Fetch successful ✅\n")

    # 4. DELETE DATA
    print("Deleting inserted row...")
    cur.execute("DELETE FROM bot_test WHERE id = %s;", (inserted_id,))
    conn.commit()
    print("Delete successful ✅\n")

    # 5. VERIFY DELETE
    print("Verifying delete...")
    cur.execute("SELECT * FROM bot_test WHERE id = %s;", (inserted_id,))
    result = cur.fetchone()
    print("Result:", result)  # should be None

    # CLEAN UP
    cur.close()
    conn.close()
    print("\nDatabase test completed 🎉")

if __name__ == "__main__":
    main()
from utils.database import DatabaseManager

db = DatabaseManager("game.db")

# Query the catalog
db.cursor.execute("SELECT * FROM cards_catalog")
rows = db.cursor.fetchall()

if not rows:
    print("❌ The catalog is empty!")
else:
    print(f"✅ Found {len(rows)} cards in the catalog:\n")
    for row in rows:
        # row[0] is ID, row[1] is Name, row[2] is Rarity, etc.
        print(f"ID: {row[0]} | Name: {row[1]} | Rarity: {row[2]}")
        print(f"URL: {row[3]}")
        print("-" * 30)
from utils.database import DatabaseManager

def register_initial_cards():
    db = DatabaseManager("game.db")

    # Define your cards here in a list of dictionaries
    new_cards = [
        {
            "name": "Green Tea",
            "rarity": "C",
            "url": "https://ik.imagekit.io/rnomfb5zn/cardgames/C_0004.png",
            "desc": "文蘭Cypher-主唱"
        },
        {
            "name": "Horus-Phoenix",
            "rarity": "A",
            "url": "https://ik.imagekit.io/rnomfb5zn/cardgames/A_0002.png",
            "desc": "The time when Horus become Phoenix to save the world..."
        },
        {
            "name": "Justlive1995-Gekko",
            "rarity": "A",
            "url": "https://ik.imagekit.io/rnomfb5zn/cardgames/A_0003.png",
            "desc": "Justlive1995 likes to play with his little fellas.."
        }
    ]

    for card in new_cards:
        # Check if the card already exists to avoid duplicates
        db.cursor.execute("SELECT 1 FROM cards_catalog WHERE name = ?", (card['name'],))
        if db.cursor.fetchone() is None:
            db.add_card_to_catalog(
                card['name'], 
                card['rarity'], 
                card['url'], 
                card['desc']
            )
            print(f"✅ Registered: {card['name']}")
        else:
            print(f"⚠️ Skipped (Already exists): {card['name']}")

if __name__ == "__main__":
    register_initial_cards()
import discord
from datetime import datetime
import random
from utils.database import DatabaseManager  # Importing your class

db = DatabaseManager()


def pull_card():
    rarities = ["D", "C", "B", "A","S"]
    # These weights determine the probability
    weights = [64, 20, 10, 5, 1] 
    
    # k=1 means we want one result. It returns a list, so we take index [0]
    result = random.choices(rarities, weights=weights, k=1)[0]

    return result

# We define the function here
def create_ai_card(user_name,user_id):
    rarity = pull_card()
    card = db.get_random_card_by_rarity(rarity)
    card_id, name, rarity, url, desc = card
    db.add_to_inventory(user_id, card_id)
    
    embed = discord.Embed(
        title="✨ Congratulation! You got:",
        description='`'+desc+'`',
        color=discord.Color.red(),
        timestamp=datetime.now()
    )
    
    embed.set_author(name=f"Replying to {user_name}")
    embed.set_footer(text="MIDV cardgames")
    embed.set_image(url=url)

    
    return embed

if __name__ == "__main__":

    print("ok")
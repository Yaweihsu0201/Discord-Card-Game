import discord
from datetime import datetime
import random
from utils.database_online import DatabaseManager  # Importing your class

db = DatabaseManager()


def pull_card(mode: str):
    rarities = ["D", "C", "B", "A","S"]
    # These weights determine the probability
    basic = [64, 20, 10, 5, 1] 
    exclusive = [0, 50, 25, 20, 5]
    premium = [0, 0, 50, 30, 20]
    # k=1 means we want one result. It returns a list, so we take index [0]
    if mode == "basic":
        result = random.choices(rarities, weights=basic, k=1)[0]
    if mode == "exclusive":
        result = random.choices(rarities, weights=exclusive, k=1)[0]
    if mode == "premium":
        result = random.choices(rarities, weights=premium, k=1)[0]
    return result

# We define the function here
def create_ai_card(user_name,user_id,mode):
    rarity = pull_card(mode)
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

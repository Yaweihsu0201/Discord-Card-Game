from PIL import Image
import requests
from io import BytesIO
import io
import discord
from collections import Counter

def sort_card(inventory_data):
    rarity_order = {"S": 0, "A": 1, "B": 2, "C": 3, "D": 4}

    #Sort the list
    sorted_inventory = sorted(
        inventory_data, 
        key=lambda x: (rarity_order.get(x[1], 99), x[0])
    )
    return sorted_inventory

def create_inventory_image(inventory_data,user_name):
        # Initialize your lists
    details = [] # This will store [name, rarity]
    card_urls = []    # This will store the url string
    inventory_data = sort_card(inventory_data)
    for row in inventory_data:
        # row[0] is name, row[1] is rarity, row[2] is image_url
        details.append([row[0], row[1]])
        card_urls.append(row[2])
    # 1. Create a blank dark background (e.g., 5 cards wide)
    canvas = Image.new('RGB', (500, 300), (30, 33, 36)) 
    
    x_offset = 10
    y_offset = 10

    card_urls = list(dict.fromkeys(card_urls))
    for url in card_urls[:10]: # Let's just do the first 10 for now
        # 2. Download the card image from your hosting
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).resize((80, 120))
        
        # 3. Paste it onto the canvas
        canvas.paste(img, (x_offset, y_offset))
        
        x_offset += 90
        if x_offset > 450: # Wrap to next row
            x_offset = 10
            y_offset += 130
    names = [item[0] for item in details]
    counts = Counter(names)
    inventory_string = ", ".join([f"**{name}**: {count}" for name, count in counts.items()])

    # 1. Save canvas to a "Buffer" (memory) instead of just a file
    # This avoids hard drive errors and is faster
    img_binary = io.BytesIO()
    canvas.save(img_binary, format='PNG')
    img_binary.seek(0)
    
    # 2. Create the discord File object
    file = discord.File(fp=img_binary, filename="inventory.png")

    # 3. Create the Embed and link it to the attachment
    embed = discord.Embed(
        title=f"✨ {user_name}'s Collection",
        #description=inventory_string,
        color=discord.Color.red(),
    )
    # This MUST match the filename in step 2
    embed.set_image(url="attachment://inventory.png")
    
    # Return both as a pair (tuple)
    return embed, file
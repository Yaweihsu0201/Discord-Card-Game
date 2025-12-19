import discord
from discord.ext import commands
import asyncio
from utils.card import create_ai_card
from utils.database_online import DatabaseManager
from utils.show_inventory import create_inventory_image
import os
from dotenv import load_dotenv

from keep_alive import keep_alive

load_dotenv()

db = DatabaseManager()

# IMPORTANT: Reset this token on the Discord Developer Portal!
TOKEN = os.getenv("DISCORD_TOKEN")

#keep_alive()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()  # ⭐ 很重要（Slash Command）
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # ⭐ 一定要加這行，否則 commands / cogs 會失效
    await bot.process_commands(message)

    if message.content.startswith("!pull"):
        user_name = message.author.display_name
        user_id = message.author.id
        can_pull, time_remained = db.check_and_update_cooldown(user_id=user_id)
        if can_pull:
            my_embed = create_ai_card(user_name,user_id)
            await message.channel.send(embed=my_embed)
        else:
            await message.channel.send("You have reached your daily limited, please wait")
        return
    if message.content.startswith("!list"):
        inventory_data = db.get_user_inventory(message.author.id)
        if not inventory_data:
            return await message.channel.send("Your inventory is empty!")

        # Call your function and unpack the two items
        embed, file = create_inventory_image(inventory_data,message.author.display_name)
        
        # You must send the file and embed together
        await message.channel.send(embed=embed, file=file)
    
    if message.content.startswith("!test"):
        user_name = message.author.display_name
        user_id = message.author.id
        my_embed = create_ai_card(user_name,user_id)
        await message.channel.send(embed=my_embed)
        return
    
async def main():
    await bot.load_extension("cogs.blackjack_pvp")
    await bot.load_extension("cogs.blackjack_invite")
    await bot.start(TOKEN)

asyncio.run(main())
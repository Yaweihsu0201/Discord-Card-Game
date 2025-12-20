import discord
from discord.ext import commands
import asyncio
from utils.card import create_ai_card
from utils.database_online import DatabaseManager
from utils.show_inventory import create_inventory_image, list_inventory
import os
from dotenv import load_dotenv

from keep_alive import keep_alive

load_dotenv()

db = DatabaseManager()

# IMPORTANT: Reset this token on the Discord Developer Portal!
TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_IDS = os.getenv("ADMIN_IDS") 

SELL_PRICE_BY_RARITY = {
    "S+": 1000,
    "S": 500,
    "A": 300,
    "B": 150,
    "C": 75,
    "D": 25,
}


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
    if message.content.startswith("!hi"):
        await message.channel.send("hello")
        return

    #daily drop
    if message.content.startswith("!daily"):
        user_name = message.author.display_name
        user_id = message.author.id
        remaining = db.get_daily_remaining(message.author.id)
        if remaining <=0:
            await message.reply("❌ No daily pulls left!")
            return
        else:
            my_embed = create_ai_card(user_name,user_id)
            db.consume_daily_pull(message.author.id)
            await message.channel.send(f"⏳ Daily remaining: {remaining-1} times")
            await message.channel.send(embed=my_embed)
            return

    #drop using money
    if message.content.startswith("!drop"):
        user_name,user_id = message.author.display_name, message.author.id
        balance = db.check_balance(user_id)
        if balance < 100:
            await message.reply("❌ You don't have enough money! (at least 100$)")
        else:
            my_embed = create_ai_card(user_name,user_id)
            db.manage_balance(message.author.id,"sub",100)
            await message.channel.send(f"💰 Your balance now: {balance-100}$")
            await message.channel.send(embed=my_embed)
            return

    #sell a card
    if message.content.startswith("!sell"):
        parts = message.content.split()

        if len(parts) != 3:
            await message.reply(
                "❌ Usage: `!sell <card_id> <amount>`",
                mention_author=False
            )
            return

        # Parse card_id
        try:
            card_id = int(parts[1])
            amount = int(parts[2])
        except ValueError:
            await message.reply(
                "❌ Card ID must be a number.",
                mention_author=False
            )
            return
            
        if amount <= 0:
            await message.reply(
                "❌ Amount must be greater than 0.",
                mention_author=False
            )
            return

        user_id = message.author.id

        # 1️⃣ Get the card
        owned_cards = db.get_cards_by_card_id(user_id, card_id)
        
        if not owned_cards or len(owned_cards) < amount:
            await message.reply(
                f"❌ You don't own **{amount}** copies of this card.",
                mention_author=False
            )
            return

        card = owned_cards[0]
        rarity = card["rank"]
        card_name = card["name"]
        await message.channel.send("card_name"+"rarity")
        # 2️⃣ Determine sell price
        sell_price = SELL_PRICE_BY_RARITY.get(rarity)
        if sell_price is None:
            await message.reply(
                "❌ This card cannot be sold.",
                mention_author=False
            )
            return
        total_price = sell_price * amount
        
        # 3️⃣ Remove card
        for _ in range(amount):
            db.remove_from_inventory_by_card_id(user_id, card_id)
        if not removed:
            await message.reply(
                "❌ Failed to remove card (try again).",
                mention_author=False
            )
            return
        await message.channel.send("cards removed")
        # 4️⃣ Add balance
        db.manage_balance(user_id, "add", total_price)

        # 5️⃣ Confirm
        await message.reply(
            f"💸 Sold **{amount}× {card_name}** ({rarity}) for **${total_price}**!",
            mention_author=False
        )

    if message.content.startswith("!collection"):
        inventory_data = db.get_user_inventory(message.author.id)
        if not inventory_data:
            return await message.channel.send("Your inventory is empty!")

        # Call your function and unpack the two items
        embed, file = create_inventory_image(inventory_data,message.author.display_name)
        
        # You must send the file and embed together
        await message.channel.send(embed=embed, file=file)
    if message.content.startswith("!list"):
        inventory_data = db.get_user_inventory(message.author.id)
        user_balance = db.check_balance(message.author.id)
        remaining = db.get_daily_remaining(message.author.id)
        if not inventory_data:
            return await message.channel.send("Your inventory is empty!")
        embed =  list_inventory(inventory_data,message.author.display_name,user_balance,remaining)
        await message.channel.send(embed=embed)

    
    if message.content.startswith("!test"):
        user_name = message.author.display_name
        user_id = message.author.id
        my_embed = create_ai_card(user_name,user_id)
        await message.channel.send(embed=my_embed)
        return
    if message.content.startswith("!add"):
        # Permission check (optional but recommended)
        if str(message.author.id) != ADMIN_IDS:
            await message.channel.send("❌ You don't have permission to use this command.")
            return

        parts = message.content.split()

        # !add @user amount  → must be exactly 3 parts
        if len(parts) != 3:
            await message.channel.send("❌ Usage: `!add @user amount`")
            return

        # 1️⃣ Get mentioned user
        if not message.mentions:
            await message.channel.send("❌ Please mention a user.")
            return

        target_user = message.mentions[0]

        # 2️⃣ Parse amount
        try:
            amount = int(parts[2])
            if amount <= 0:
                raise ValueError
        except ValueError:
            await message.channel.send("❌ Amount must be a positive number.")
            return

        # 3️⃣ Update balance
        db.manage_balance(target_user.id, "add", amount)

        # 4️⃣ Confirm
        await message.channel.send(
            f"✅ Added 💰 **${amount}** to **{target_user.display_name}**"
        )

        return
    if message.content.startswith("!help"):
        embed = discord.Embed(
            title="📖 Bot Commands Help",
            description="Here are all available commands",
            color=0x5865F2
        )

        embed.add_field(
            name="🎴 Card / Gacha",
            value=(
                "`!daily` → Daily free pull\n"
                "`!drop` → Pull a card (cost $100)\n"
                "`!sell <card_id>` → Sell a card"
            ),
            inline=False
        )

        embed.add_field(
            name="🎒 Inventory",
            value=(
                "`!collection` → Show card collection image\n"
                "`!list` → List all owned cards"
            ),
            inline=False
        )

        embed.add_field(
            name="💰 Economy",
            value=(
                "`!daily` → Limited daily pulls\n"
                "`!drop` → Spend money to pull"
            ),
            inline=False
        )

        embed.add_field(
            name="🎮 Games",
            value=(
                "`/blackjack` → Play Blackjack (Slash Command)\n"
                "`/blackjack_invite` → Invite others"
            ),
            inline=False
        )

        embed.add_field(
            name="🛠 Admin",
            value="`!add @user amount` → Add money (Admin only)",
            inline=False
        )

        embed.set_footer(text="Use commands with ! or /")

        await message.channel.send(embed=embed)
        return

    
async def main():
    await bot.load_extension("cogs.blackjack_pvp")
    await bot.load_extension("cogs.blackjack_invite")
    await bot.start(TOKEN)

asyncio.run(main())

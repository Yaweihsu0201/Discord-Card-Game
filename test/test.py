import os
from dotenv import load_dotenv

load_dotenv() # This MUST happen before the next line
print(os.getenv("DISCORD_TOKEN"))
print(f"Does .env exist here? {os.path.exists('.env')}")
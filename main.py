import asyncio
import os
import logging
import datetime
import aiohttp

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Configuration from environment variables.
TOKEN = os.getenv("DISCORD_TOKEN")
BOT_PREFIX = os.getenv("BOT_PREFIX", "!")
STAT_CHANNEL_ID = int(os.getenv("STAT_CHANNEL_ID", "0"))
API_ENDPOINT = os.getenv("API_ENDPOINT")
API_KEY = os.getenv("NIJII_API_KEY")  # The API key used in the request

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

logging.basicConfig(level=logging.INFO)

# List of initial extensions (cogs) to load.
initial_extensions = [
    "cogs.welcome",
    "cogs.images",
    "cogs.moderation",
    "cogs.logs",
    "cogs.ready"
]

async def load_extensions() -> None:
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            logging.info(f"Extension {extension} loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading extension {extension}: {e}")

async def main() -> None:
    await load_extensions()
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
logger = logging.getLogger(__name__)

class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Retrieve the welcome channel ID from the environment and convert it to an integer.
        self.welcome_channel_id = int(os.getenv("WELCOME_CHANNEL_ID", "0"))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.get_channel(self.welcome_channel_id)
        if channel:
            embed = discord.Embed(
                title="Welcome!",
                description=f"Hello {member.mention}, welcome to our server! Enjoy your stay.",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            await channel.send(embed=embed)
        else:
            logger.error("Welcome channel not found in guild: %s", member.guild.name)

async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))

from __future__ import annotations

import asyncio
import os
import logging
import datetime
import aiohttp

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class Ready(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.stats_message: discord.Message | None = None
        self.stat_channel_id: int = int(os.getenv("STAT_CHANNEL_ID", "0"))
        self.api_endpoint: str = os.getenv("API_ENDPOINT")
        self.api_key: str = os.getenv("NIJII_API_KEY")
        self.task: asyncio.Task | None = None

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        logger.info(f"[Ready Cog] Logged in as {self.bot.user} (ID: {self.bot.user.id})")
        try:
            synced = await self.bot.tree.sync()
            logger.info(f"Synced {len(synced)} commands")
        except Exception as e:
            logger.error("Failed to sync commands: %s", e)
            
        if self.task is None:
            self.task = self.bot.loop.create_task(self.update_stats_task())

    async def update_stats_task(self) -> None:
        while True:
            try:
                headers = {"X-API-KEY": self.api_key} if self.api_key else {}
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.api_endpoint, headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()

                            global_stats = data.get("globalStats", {})
                            total_requests = global_stats.get("totalRequests", "None")
                            total_images = global_stats.get("totalImages", "None")
                            total_users = global_stats.get("totalUsers", "None")

                            api_timestamp = data.get("timestamp")
                            uptime = data.get("uptime")
                            if api_timestamp and uptime:
                                start_time = int(api_timestamp - uptime)
                                uptime_str = f"<t:{start_time}:R>"
                            else:
                                uptime_str = "Unknown"

                            embed = discord.Embed(
                                title="API Stats",
                                color=discord.Color.green(),
                                timestamp=datetime.datetime.utcnow()
                            )
                            embed.description = (
                                f"**Total Requests:** {total_requests}\n"
                                f"**Total Images:** {total_images}\n"
                                f"**Total Users:** {total_users}\n"
                                f"**Online for:** {uptime_str}"
                            )
                        else:
                            embed = discord.Embed(
                                title="API is offline",
                                description="Error retrieving API stats.",
                                color=discord.Color.red(),
                                timestamp=datetime.datetime.utcnow()
                            )
            except Exception as e:
                logger.error("Exception during API stats retrieval: %s", e)
                embed = discord.Embed(
                    title="API is offline",
                    description=f"Exception: {e}",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.utcnow()
                )

            embed.set_footer(text="Last update:")
            stat_channel = self.bot.get_channel(self.stat_channel_id)
            if stat_channel:
                if self.stats_message is None:
                    try:
                        self.stats_message = await stat_channel.send(embed=embed)
                    except Exception as e:
                        logger.error("Failed to send stats message: %s", e)
                else:
                    try:
                        await self.stats_message.edit(embed=embed)
                    except Exception as e:
                        logger.error("Failed to update stats message: %s", e)
            else:
                logger.error("Stats channel not found (ID: %s)", self.stat_channel_id)
            await asyncio.sleep(300)  # 5 minutes

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ready(bot))

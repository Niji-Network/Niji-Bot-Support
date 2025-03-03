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
        # Start the background task only once.
        if self.task is None:
            self.task = self.bot.loop.create_task(self.update_stats_task())

    async def update_stats_task(self) -> None:
        """Periodically fetch API stats and update the stats embed every 5 minutes."""
        while True:
            embed: discord.Embed
            try:
                headers = {"X-API-KEY": self.api_key} if self.api_key else {}
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.api_endpoint, headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()

                            # Global stats
                            global_stats = data.get("globalStats", {})
                            total_requests = global_stats.get("totalRequests", "None")
                            total_images = global_stats.get("totalImages", "None")
                            total_users = global_stats.get("totalUsers", "None")

                            # API response timestamp (for "Online from")
                            api_timestamp = data.get("timestamp")
                            if api_timestamp:
                                ts = int(api_timestamp)
                                online_from = f"<t:{ts}:R>"
                            else:
                                online_from = "Unknown"

                            # Extra system stats
                            cpu_usage = data.get("cpu_usage")
                            cpu_count = data.get("cpu_count", "None")
                            cpu_freq = data.get("cpu_frequency", {}).get("current", "None")
                            load_avg = data.get("load_average", [])
                            load_avg_str = ", ".join(f"{x:.2f}" for x in load_avg) if load_avg else "None"

                            total_memory = data.get("total_memory", "None")
                            used_memory = data.get("used_memory", "None")
                            memory_percent = data.get("memory_percent", "None")

                            disk_total = data.get("disk_total", "None")
                            disk_used = data.get("disk_used", "None")
                            disk_free = data.get("disk_free", "None")
                            disk_percent = data.get("disk_percent", "None")

                            process_count = data.get("process_count", "None")

                            net_io = data.get("net_io", {})
                            bytes_sent = net_io.get("bytes_sent", "None")
                            bytes_recv = net_io.get("bytes_recv", "None")

                            embed = discord.Embed(
                                title="API is online",
                                color=discord.Color.green(),
                                timestamp=datetime.datetime.utcnow()
                            )
                            # Global stats in description
                            embed.description = (
                                f"**Total Requests:** {total_requests}\n"
                                f"**Total Images:** {total_images}\n"
                                f"**Total Users:** {total_users}\n"
                            )

                            # Add extra system stats as fields
                            embed.add_field(
                                name="CPU",
                                value=(
                                    f"Usage: {cpu_usage * 100:.1f}%" if isinstance(cpu_usage, (int, float)) else "None"
                                    f"\nCores: {cpu_count}"
                                    f"\nFrequency: {cpu_freq:.2f} MHz" if isinstance(cpu_freq, (int, float)) else "\nFrequency: None"
                                ),
                                inline=True,
                            )
                            embed.add_field(
                                name="Load Average",
                                value=load_avg_str,
                                inline=True,
                            )
                            embed.add_field(
                                name="Memory",
                                value=(
                                    f"Used: {used_memory} MB / Total: {total_memory} MB\n"
                                    f"Usage: {memory_percent}%"
                                ),
                                inline=True,
                            )
                            embed.add_field(
                                name="Disk",
                                value=(
                                    f"Used: {disk_used} GB / Total: {disk_total} GB\n"
                                    f"Usage: {disk_percent}%"
                                ),
                                inline=True,
                            )
                            embed.add_field(
                                name="Processes",
                                value=f"{process_count}",
                                inline=True,
                            )
                            embed.add_field(
                                name="Network",
                                value=(
                                    f"Sent: {bytes_sent} bytes\n"
                                    f"Recv: {bytes_recv} bytes"
                                ),
                                inline=True,
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

            embed.set_footer(text=f"Last update:")

            # Retrieve the channel where stats should be posted/updated.
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
            await asyncio.sleep(300)  # Wait 5 minutes before rechecking.

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ready(bot))

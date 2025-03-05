import discord
from discord.ext import commands
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="kick",
        description="Kick a user from the server"
    )
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = None) -> None:
        try:
            await member.kick(reason=reason)
            await ctx.send(f"> {member.mention} has been kicked from the server.")
        except Exception as e:
            logger.error("Error kicking user %s: %s", member, e)
            await ctx.send("> Error while kicking the user.")

    @commands.hybrid_command(
        name="ban",
        description="Ban a user from the server"
    )
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = None) -> None:
        try:
            await member.ban(reason=reason)
            await ctx.send(f"> {member.mention} has been banned from the server.")
        except Exception as e:
            logger.error("Error banning user %s: %s", member, e)
            await ctx.send("> Error while banning the user.")

    @commands.hybrid_command(
        name="timeout",
        description="Timeout a user for a specified duration (in seconds)"
    )
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx: commands.Context, member: discord.Member, duration: int, *, reason: str = None) -> None:
        try:
            timeout_until = datetime.utcnow() + timedelta(seconds=duration)
            await member.edit(timeout=timeout_until, reason=reason)
            await ctx.send(f"> {member.mention} has been timed out for {duration} seconds.")
        except Exception as e:
            logger.error("Error timing out user %s: %s", member, e)
            await ctx.send("> Error while timing out the user.")

    @commands.hybrid_command(
        name="clear",
        description="Clear a specified number of messages from the channel"
    )
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount: int) -> None:
        try:
            deleted = await ctx.channel.purge(limit=amount)
            await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)
        except Exception as e:
            logger.error("Error clearing messages in channel %s: %s", ctx.channel, e)
            await ctx.send("> Error clearing messages.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot))
import discord
from discord.ext import commands
from dotenv import load_dotenv
import datetime
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class Logs(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        # Load the log channel IDs from the environment variables.
        self.public_logs_channel_id = int(os.getenv("PUBLIC_LOG_CHANNEL_ID", "0"))
        self.private_logs_channel_id = int(os.getenv("PRIVATE_LOG_CHANNEL_ID", "0"))

    async def log_to_channel(self, channel_id: int, embed: discord.Embed) -> None:
        channel = self.bot.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)
        else:
            logger.error("Log channel with ID %s not found.", channel_id)

    # Public logs for member join and leave events.
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        embed = discord.Embed(
            title="Member Joined",
            description=f"User: {member.mention} ({member})\nID: {member.id}",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        await self.log_to_channel(self.public_logs_channel_id, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        embed = discord.Embed(
            title="Member Left",
            description=f"User: {member.mention} ({member})\nID: {member.id}",
            color=discord.Color.red(),
            timestamp=datetime.datetime.utcnow()
        )
        await self.log_to_channel(self.public_logs_channel_id, embed)

    # Private logs for command usage and errors.
    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context) -> None:
        embed = discord.Embed(
            title="Command Used",
            description=(
                f"**Command:** `{ctx.command}`\n"
                f"**User:** {ctx.author} ({ctx.author.id})\n"
                f"**Channel:** {ctx.channel}\n"
                f"**Guild:** {ctx.guild.name if ctx.guild else 'DM'}"
            ),
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.utcnow()
        )
        await self.log_to_channel(self.private_logs_channel_id, embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        embed = discord.Embed(
            title="Command Error",
            description=(
                f"**Command:** `{ctx.command}`\n"
                f"**User:** {ctx.author} ({ctx.author.id})\n"
                f"**Error:** `{error}`"
            ),
            color=discord.Color.orange(),
            timestamp=datetime.datetime.utcnow()
        )
        await self.log_to_channel(self.private_logs_channel_id, embed)

    # Private logs for message edits and deletions.
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.author.bot:
            return
        embed = discord.Embed(
            title="Message Edited",
            description=(
                f"**User:** {before.author} ({before.author.id})\n"
                f"**Channel:** {before.channel}"
            ),
            color=discord.Color.gold(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="Before", value=before.content or "None", inline=False)
        embed.add_field(name="After", value=after.content or "None", inline=False)
        await self.log_to_channel(self.private_logs_channel_id, embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        embed = discord.Embed(
            title="Message Deleted",
            description=(
                f"**User:** {message.author} ({message.author.id})\n"
                f"**Channel:** {message.channel}"
            ),
            color=discord.Color.dark_red(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="Content", value=message.content or "None", inline=False)
        await self.log_to_channel(self.private_logs_channel_id, embed)

    # Private logs for guild member updates (nickname, roles, etc.)
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        changes = []
        if before.nick != after.nick:
            changes.append(f"Nickname changed: `{before.nick}` → `{after.nick}`")
        # Compare roles
        before_roles = {role.id for role in before.roles}
        after_roles = {role.id for role in after.roles}
        added_roles = after_roles - before_roles
        removed_roles = before_roles - after_roles
        if added_roles:
            added_names = [discord.utils.get(after.roles, id=r).name for r in added_roles]
            changes.append(f"Roles added: {', '.join(added_names)}")
        if removed_roles:
            removed_names = [discord.utils.get(before.roles, id=r).name for r in removed_roles]
            changes.append(f"Roles removed: {', '.join(removed_names)}")

        if changes:
            embed = discord.Embed(
                title="Member Updated",
                description=f"User: {after.mention} ({after})\nID: {after.id}",
                color=discord.Color.purple(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="Changes", value="\n".join(changes), inline=False)
            await self.log_to_channel(self.private_logs_channel_id, embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Logs(bot))
import discord
from discord.ext import commands
import aiohttp
import os
import random
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class Images(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.api_key = os.getenv("NIJII_API_KEY")
        self.base_endpoint = "https://api.nijii.xyz/v1/img/{category}"
        self.allowed_categories = ["random", "waifu", "husbando"]
        self.session = aiohttp.ClientSession()

    def cog_unload(self) -> None:
        # Close the HTTP session when the cog is unloaded.
        if self.session:
            self.bot.loop.create_task(self.session.close())

    @commands.hybrid_command(
        name="image",
        description="Send a random image from a given category"
    )
    @discord.app_commands.describe(
        category="Category of the image: random, waifu, or husbando"
    )
    @discord.app_commands.choices(category=[
        discord.app_commands.Choice(name="random", value="random"),
        discord.app_commands.Choice(name="waifu", value="waifu"),
        discord.app_commands.Choice(name="husbando", value="husbando")
    ])
    async def image(self, ctx: commands.Context, category: str = "random") -> None:
        category = category.lower()
        if category not in self.allowed_categories:
            await ctx.send("Invalid category. Please choose one of: random, waifu, husbando.")
            return

        url = self.base_endpoint.format(category=category)
        headers = {"X-API-KEY": self.api_key} if self.api_key else {}

        try:
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get("items", [])
                    if items:
                        chosen_item = random.choice(items)
                        image_url = chosen_item.get("url")
                        if image_url:
                            # Extract additional info, defaulting to "None" when absent.
                            anime = chosen_item.get("anime") or "None"
                            nsfw = chosen_item.get("nsfw")
                            nsfw_text = "Yes" if nsfw else "No"
                            characters = chosen_item.get("character")
                            characters_text = ", ".join(characters) if characters else "None"
                            tags = chosen_item.get("tags")
                            tags_text = ", ".join(tags) if tags else "None"

                            embed = discord.Embed(
                                title=f"{category.capitalize()} Image",
                                description=(
                                    f"> **Anime:** {anime}\n"
                                    f"> **NSFW:** {nsfw_text}\n"
                                    f"> **Characters:** {characters_text}\n"
                                    f"> **Tags:** {tags_text}\n",
                                    f"> **URL:** [Click here]({image_url})",
                                ),
                                color=discord.Color.blurple()
                            )
                            embed.set_image(url=image_url)
                            await ctx.send(embed=embed)
                        else:
                            await ctx.send("> No image found in the chosen item.")
                    else:
                        await ctx.send("> No images found.")
                else:
                    await ctx.send("> Error retrieving the image.")
        except Exception as e:
            logger.error("Exception occurred while fetching image: %s", e)
            await ctx.send("> An error occurred while retrieving the image.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Images(bot))

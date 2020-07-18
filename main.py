import os

import discord
from discord.ext import commands

import card_data
import card_art


bot = commands.Bot(command_prefix=os.environ["BOT_PREFIX"])


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
async def invite(ctx):
    """Generate a link to invite me to your server"""

    app_info = await bot.application_info()
    link = f"https://discord.com/api/oauth2/authorize?client_id={app_info.id}&permissions=18432&scope=bot"
    await ctx.send(f"Invite me to your server: <{link}>")


@bot.command()
async def cards(ctx, *, query: str):
    """List all matching cards"""

    async with ctx.typing():
        cards = await card_data.get()
    results = card_data.find(cards, query, num_results=10)
    if not results:
        await ctx.send(f'Found no cards matching "{query}"')
    else:
        await ctx.send(
            "Found these cards:\n"
            + "\n".join("{card_id}: {card_name}".format(**card) for card in results)
        )


@bot.command()
async def card(ctx, *, query: str):
    """Display a card's stats and text"""

    async with ctx.typing():
        cards = await card_data.get()
    results = card_data.find(cards, query, num_results=1)
    if not results:
        await ctx.send(f'Found no cards matching "{query}"')
    else:
        [result] = results
        embed = discord.Embed.from_dict(card_data.info_embed(result))
        await ctx.send(embed=embed)


@bot.command()
async def flavor(ctx, *, query: str):
    """Display a card's flavortext"""

    async with ctx.typing():
        cards = await card_data.get()
    results = card_data.find(cards, query, num_results=1)
    if not results:
        await ctx.send(f'Found no cards matching "{query}"')
    else:
        [result] = results
        embed = discord.Embed.from_dict(card_data.flavor_embed(result))
        await ctx.send(embed=embed)


async def art_gen(ctx, query: str, which: str):
    """Helper function for art commands"""

    async with ctx.typing():
        cards = await card_data.get()

    results = card_data.find(cards, query, num_results=1)
    if not results:
        await ctx.send(f'Found no cards matching "{query}"')
        return
    [result] = results
    card_name = result["card_name"]

    async with ctx.typing():
        image = await card_art.get_asset(result["card_id"], which)

    if image is None:
        await ctx.send(f'Failed to get card art for "{card_name}"')
    else:
        await ctx.send(card_name, file=discord.File(image, "0.png"))


@bot.command()
async def art(ctx, *, query: str):
    """Display a card's base art"""

    await art_gen(ctx, query, "0")


@bot.command()
async def evoart(ctx, *, query: str):
    """Display a card's evolved art"""

    await art_gen(ctx, query, "1")


bot.run(os.environ["DISCORD_TOKEN"])

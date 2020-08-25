import os

import discord
from discord.ext import commands

import card_data
import card_art
import deck_code


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
    """List all matching cards by name"""

    async with ctx.typing():
        cards = await card_data.get()
    results = card_data.find(cards, query, num_results=10)
    if not results:
        await ctx.send(f'Found no cards matching "{query}"')
    else:
        await ctx.send(
            "Found these cards:\n"
            + "\n".join(card_data.effective_card_name(card) for card in results)
        )


@bot.command(aliases=["text"])
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


@bot.command(aliases=["flavor", "flair"])
async def flavortext(ctx, *, query: str):
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
    card_name = card_data.effective_card_name(result)

    async with ctx.typing():
        image = await card_art.get_asset(result["card_id"], which)

    if image is None:
        await ctx.send(f'Failed to get card art for "{card_name}"')
    else:
        await ctx.send(card_name, file=discord.File(image, "0.png"))


@bot.command(aliases=["img"])
async def art(ctx, *, query: str):
    """Display a card's base art"""

    await art_gen(ctx, query, "0")


@bot.command(aliases=["evoimg", "evo"])
async def evoart(ctx, *, query: str):
    """Display a card's evolved art"""

    await art_gen(ctx, query, "1")


@bot.command(aliases=["filter", "list"])
async def search(ctx, *query):
    """Search by full text and list all matching cards.

    Examples:
    - search 6pp shadow gold spell
    - search earth sigil
    - search havencraft "repair mode"
    - search legendary "steel rebellion"
    """

    async with ctx.typing():
        cards = await card_data.get()
    results = card_data.search(cards, query)
    if not results:
        await ctx.send(f'Found no cards matching "{query}"')
    else:
        max_results = 20
        lines = [f"Found {len(results)} cards:"]
        lines += [card_data.effective_card_name(card) for card in results[:max_results]]
        if len(results) > max_results:
            lines += [f"({len(results) - max_results} more)"]
        await ctx.send("\n".join(lines))


@bot.command(aliases=["deck", "code"])
async def deckcode(ctx, code: str):
    """Look up a deck code."""

    result = await deck_code.get(code)
    embed = discord.Embed.from_dict(deck_code.embed(result))
    await ctx.send(embed=embed)


@bot.command(hidden=True)
async def eggsplosion(ctx):
    async with ctx.typing():
        cards = await card_data.get()
    card = card_data.eggsplosion_card(cards)
    await ctx.send(f"{card} dies to Eggsplosion")


@bot.command(aliases=["bugreport", "bug", "report"])
async def feedback(ctx, *, message: str):
    """Report feedback to the bot dev"""

    log_channel = bot.get_channel(int(os.environ["LOG_CHANNEL"]))
    await log_channel.send(
        f"Feedback from {ctx.author} in {ctx.guild} {ctx.channel}: ```{message}```"
    )


@bot.event
async def on_command_error(ctx, error):
    if "LOG_CHANNEL" in os.environ:
        log_channel = bot.get_channel(int(os.environ["LOG_CHANNEL"]))
        await log_channel.send(
            f"Error from {ctx.author} in {ctx.guild} {ctx.channel}: ```{error}```"
        )
    else:
        await commands.Bot.on_command_error(bot, ctx, error)


bot.run(os.environ["DISCORD_TOKEN"])

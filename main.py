import os
import asyncio

import discord
from discord.ext import commands

import card_data
import card_art
import card_voice
import sleeves
import deck_code

command_prefix = os.environ["BOT_PREFIX"].split()

bot = commands.Bot(
    command_prefix=command_prefix,
    description=os.environ.get("DESCRIPTION", "Shadowverse info bot"),
)


class CardNotFoundError(Exception):
    def __init__(self, query: list):
        self.query = query
        super().__init__(query)


class CardArtError(Exception):
    def __init__(self, card_id: int, card_name: str):
        self.card_id = card_id
        self.card_name = card_name
        super().__init__(card_id, card_name)


class DeckCodeError(Exception):
    def __init__(self, deck_code: str, errors: list):
        self.deck_code = deck_code
        self.errors = errors
        super().__init__(deck_code, errors)


# Hack: avoid raising UnexpectedQuoteError
commands.view._all_quotes = set()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if os.environ.get("DEV") is None:
        activity = discord.Game(name=f"{command_prefix[0]}help")
        await bot.change_presence(activity=activity)


@bot.command()
async def invite(ctx):
    """Generate a link to invite me to your server"""

    app_info = await bot.application_info()
    link = f"https://discord.com/api/oauth2/authorize?client_id={app_info.id}&permissions=18432&scope=bot"
    await ctx.send(f"Invite me to your server: <{link}>")


@bot.command(aliases=["list", "l", "search", "s"])
async def cards(ctx, *query):
    """List all matching cards.

    Keyword search is supported. Examples:
    - search 6pp shadow gold spell
    - search earth sigil
    - search havencraft "repair mode"
    - search legendary "steel rebellion"

    """

    async with ctx.typing():
        cards = await card_data.get()
    results = card_data.find(cards, query)
    if not results:
        raise CardNotFoundError(query)
    else:
        max_results = 20
        if len(results) <= max_results:
            lines = [f"Found {len(results)} cards:"]
            lines += [card_data.effective_card_name(card) for card in results]
            await ctx.send("\n".join(lines))
        else:
            lo = 0
            hi = max_results
            lines = [f"Found {len(results)} cards, displaying {lo+1}-{hi}:"]
            lines += [card_data.effective_card_name(card) for card in results[lo:hi]]
            msg = await ctx.send("\n".join(lines))
            await msg.add_reaction("⬅️")
            await msg.add_reaction("➡️")

            def check(reaction, user):
                return (
                    user != bot.user
                    and reaction.message.id == msg.id
                    and reaction.emoji in ["➡️", "⬅️"]
                )

            while True:
                try:
                    reaction, usr = await bot.wait_for(
                        "reaction_add", timeout=30.0, check=check
                    )
                except asyncio.TimeoutError:
                    await msg.remove_reaction("➡️", bot.user)
                    await msg.remove_reaction("⬅️", bot.user)
                    break
                else:
                    if reaction.emoji == "➡️":
                        hi = min(len(results), hi + max_results)
                        lo = hi - max_results
                    elif reaction.emoji == "⬅️":
                        lo = max(0, lo - max_results)
                        hi = lo + max_results

                    lines = [f"Found {len(results)} cards, displaying {lo+1}-{hi}:"]
                    lines += [
                        card_data.effective_card_name(card) for card in results[lo:hi]
                    ]
                    await msg.edit(content="\n".join(lines))


@bot.command(aliases=["c", "text", "t"])
async def card(ctx, *query):
    """Display a card's stats and text"""

    async with ctx.typing():
        cards = await card_data.get()
    results = card_data.find(cards, query)
    if not results:
        raise CardNotFoundError(query)
    else:
        result = results[0]
        embed = discord.Embed.from_dict(card_data.info_embed(result))
        await ctx.send(embed=embed)


@bot.command(aliases=["flavourtext", "flavor", "flavour", "flairtext", "flair", "f"])
async def flavortext(ctx, *query):
    """Display a card's flavortext"""

    async with ctx.typing():
        cards = await card_data.get()
    results = card_data.find(cards, query)
    if not results:
        raise CardNotFoundError(query)
    else:
        result = results[0]
        embed = discord.Embed.from_dict(card_data.flavor_embed(result))
        await ctx.send(embed=embed)


async def art_gen(ctx, query: list, which: str):
    """Helper function for art commands"""

    async with ctx.typing():
        cards = await card_data.get()

    results = card_data.find(cards, query)
    if not results:
        raise CardNotFoundError(query)
    result = results[0]
    card_id = result["card_id"]
    card_name = card_data.effective_card_name(result)

    async with ctx.typing():
        image = await card_art.svgdb_get(card_id, which)

    if image is None:
        raise CardArtError(card_id, card_name)
    else:
        await ctx.send(card_name, file=discord.File(image, "0.png"))


@bot.command(aliases=["v"])
async def voice(ctx, *query):
    async with ctx.typing():
        cards = await card_data.get()

    results = card_data.find(cards, query)
    if not results:
        raise CardNotFoundError(query)
    result = results[0]

    async with ctx.typing():
        embed = await card_voice.svgdb_embed(result)

    await ctx.send(embed=discord.Embed.from_dict(embed))


@bot.command(aliases=["img", "a"])
async def art(ctx, *query):
    """Display a card's base art"""

    await art_gen(ctx, query, "0")


@bot.command(aliases=["evoimg", "evo", "e"])
async def evoart(ctx, *query):
    """Display a card's evolved art"""

    await art_gen(ctx, query, "1")


@bot.command()
async def sleeve(ctx, *query):
    """Display sleeve art"""

    async with ctx.typing():
        if not query:
            image, sleeve_name = await sleeves.get_random()
        else:
            sleeve_id, sleeve_name = await sleeves.find_sleeve(query)
            if not sleeve_id:
                raise CardNotFoundError(query)
            image = await sleeves.get_asset(sleeve_id)

    if image is None:
        raise CardArtError(sleeve_id, sleeve_name)
    else:
        await ctx.send(sleeve_name, file=discord.File(image, "0.png"))


@bot.command(aliases=["deck", "code"])
async def deckcode(ctx, code: str):
    """Look up a deck code."""

    async with ctx.typing():
        result = await deck_code.get(code)

    errors = result.get("errors")
    if errors:
        raise DeckCodeError(code, errors)

    embed = discord.Embed.from_dict(deck_code.embed(result))
    await ctx.send(embed=embed)


@bot.command(hidden=True)
async def randomcard(ctx):
    async with ctx.typing():
        cards = await card_data.get()
    card = card_data.random_card(cards)
    embed = discord.Embed.from_dict(card_data.info_embed(card))
    await ctx.send(embed=embed)


@bot.command(hidden=True)
async def update(ctx):
    async with ctx.typing():
        await card_data._update()


@bot.command(hidden=True)
async def eggsplosion(ctx):
    async with ctx.typing():
        cards = await card_data.get()
    card = card_data.random_card(cards, eggsplosion=True)["card_name"]
    await ctx.send(f"{card} dies to Eggsplosion")


@bot.command(aliases=["bugreport", "bug", "report"])
async def feedback(ctx, *, message: str):
    """Report feedback to the bot dev"""

    log_channel = bot.get_channel(int(os.environ["LOG_CHANNEL"]))
    await log_channel.send(
        f"Feedback from {ctx.author} in {ctx.guild} {ctx.channel}: ```{message}```"
    )
    await ctx.send("Feedback sent. Thank you!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.CommandNotFound):
        if ctx.invoked_with in ["art1", "art2", "art3", "art4", "art5", "art6"]:
            await ctx.send(
                f"{error}\n"
                f"Tip: Use `{ctx.prefix}evoart` to look up evolved art. "
                "For alternate card art, you can specify 'alt' or the card set. Examples:\n"
                f"- `{ctx.prefix}art fairy circle alt`\n"
                f"- `{ctx.prefix}art albert leader`\n"
                f"- `{ctx.prefix}art albert prebuilt`\n"
                f"- `{ctx.prefix}art witch snap fate`\n"
            )
        else:
            await ctx.send(
                f"{error}\n"
                f"Tip: Use `{ctx.prefix}card` to look up a card. "
                f"See `{ctx.prefix}help` for other commands."
            )
        return
    elif isinstance(error, discord.ext.commands.CommandInvokeError):
        error = error.original
        if isinstance(error, CardNotFoundError):
            await ctx.send(f"Found no cards matching `{error.query}`")
        elif isinstance(error, CardArtError):
            await ctx.send(f'Failed to get card art for "{error.card_name}"')
        elif isinstance(error, DeckCodeError):
            await ctx.send(f"Failed to get deck code `{error.deck_code}`")
    if "LOG_CHANNEL" in os.environ:
        log_channel = bot.get_channel(int(os.environ["LOG_CHANNEL"]))
        await log_channel.send(
            f"Error from {ctx.author} in {ctx.guild} {ctx.channel}:\n"
            f"{ctx.message.jump_url}\n"
            f"```{repr(error)}```"
        )
    else:
        await commands.Bot.on_command_error(bot, ctx, error)


bot.run(os.environ["DISCORD_TOKEN"])

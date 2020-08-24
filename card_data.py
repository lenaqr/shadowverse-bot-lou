import random
import difflib
import aiohttp


crafts = [
    "Neutral",
    "Forestcraft",
    "Swordcraft",
    "Runecraft",
    "Dragoncraft",
    "Shadowcraft",
    "Bloodcraft",
    "Havencraft",
    "Portalcraft",
]
rarities = {
    1: "Bronze",
    2: "Silver",
    3: "Gold",
    4: "Legendary",
}
card_types = {
    1: "Follower",
    2: "Amulet",  # permanent
    3: "Amulet",  # countdown
    4: "Spell",
}
card_sets = {
    10000: "Basic",
    10001: "Classic",
    10002: "Darkness Evolved",
    10003: "Rise of Bahamut",
    10004: "Tempest of the Gods",
    10005: "Wonderland Dreams",
    10006: "Starforged Legends",
    10007: "Chronogenesis",
    10008: "Dawkbreak Nightedge",
    10009: "Brigade of the Sky",
    10010: "Omen of the Ten",
    10011: "Altersphere",
    10012: "Steel Rebellion",
    10013: "Rebirth of Glory",
    10014: "Verdant Conflict",
    10015: "Ultimate Colosseum",
    10016: "World Uprooted",
    10017: "Fortune's Hand",
    10018: "Set 18",
    10019: "Set 19",
    70001: "Prebuilt Decks 1",
    70002: "Prebuilt Decks 2",
    70003: "Anigera DIDOON Tie-In",
    70004: "Fate/stay night [Heaven's Feel] Tie-in",
    70005: "Prebuilt Decks 4",
    70006: "Prebuilt Decks 5",
    70008: "Princess Connect! Re:Dive Tie-in",
    70009: "One-Punch Man Tie-in",
    70010: "Re:ZERO Tie-in",
    70011: "Prebuilt Decks 6",
    70012: "Love Live! School Idol Festival Tie-in",
    70013: "The Melancholy of Haruhi Suzumiya Tie-in",
    70014: "Prebuilt Decks 7",
    70015: "The Idolmaster: Cinderella Girls Tie-in",
    70016: "NieR:Automata Tie-in",
    70017: "Code Geass Lelouch of the Rebellion Tie-in",
    90000: "Token",
}


_cache = None


async def _update():
    global _cache
    url = "https://shadowverse-portal.com/api/v1/cards?format=json&lang=en"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            json = await response.json()
    _cache = json["data"]["cards"]


async def get() -> list:
    """Get card info from shadowverse-portal."""
    if _cache is None:
        await _update()
    return _cache


def effective_card_name(card: dict) -> str:
    """Get the effective name of a card."""
    card_name = card["card_name"]
    if card_name is None:
        return None
    if card["card_id"] != card["base_card_id"]:
        card_set = card_sets[card["card_set_id"]]
        return card_name + f" (Alt: {card_set})"
    return card_name


def find(cards: list, query: str, *, num_results: int) -> list:
    """Find cards whose names match the query string."""
    results = []
    query_words = query.lower().split()
    for i, card in enumerate(cards):
        card_name = effective_card_name(card)
        if card_name is None:
            continue
        if query.islower():
            card_name = card_name.lower()
        if query == card_name:
            is_exact = True
            match_size = len(query)
            match_cost = len(query)
        else:
            # iterate over blocks of matching characters as returned by
            # difflib, to get
            # - "match_size", the number of matching characters
            # - "match_cost", the number of edit operations from the card name
            #   to the search query
            is_exact = False
            s = difflib.SequenceMatcher(str.isspace, query, card_name, autojunk=False)
            blocks = s.get_matching_blocks()
            match_size = 0
            match_cost = len(query)
            pos = 0
            for block in blocks:
                # we matched `block.size` characters and we skipped over the
                # substring `card_name[pos : block.b]`
                match_size += block.size
                num_unmatched_words = len(card_name[pos : block.b].split())
                if block.b < len(card_name):
                    # cost 1 per word in the skipped substring
                    match_cost += num_unmatched_words
                else:
                    # special case: we skipped over the whole rest of the
                    # string. cost 1 to skip the rest, plus 1 to skip to the
                    # end of the current word if we were in the middle of one.
                    if num_unmatched_words > 0:
                        match_cost += 1
                    if (
                        num_unmatched_words > 1
                        and pos < len(card_name)
                        and not card_name[pos].isspace()
                        and not card_name[pos] == ","
                    ):
                        match_cost += 1
                # set `pos` to the end of the matching block
                pos = block.b + block.size
            # difflib always produces a dummy block at the end.
            assert pos == len(card_name)
        card_id = card["card_id"]
        is_alt_or_token = card_id >= 700000000 or card_id != card["base_card_id"]
        key = (-is_exact, -match_size / match_cost, is_alt_or_token, -card_id)
        results.append((key, i))
    results.sort()
    return [cards[i] for (_, i) in results[:num_results]]


def reformat_text(text: str) -> str:
    """Replace shadowverse-portal's formatting markup with markdown."""
    return (
        text.replace("<br>", "\n")
        .replace("[/b][b]", "")
        .replace("[b]", "**")
        .replace("[/b]", "**")
    )


def info_embed(card: dict) -> dict:
    """Generate an embed for a card's info."""
    card_type = card_types[card["char_type"]]
    title = effective_card_name(card)
    description = (
        "{cost}pp {craft} {rarity} {card_type}\n"
        "Trait: {trait}\n"
        "Card Set: {card_set}"
    ).format(
        cost=card["cost"],
        craft=crafts[card["clan"]],
        rarity=rarities[card["rarity"]],
        card_type=card_type,
        trait=card["tribe_name"],
        card_set=card_sets[card["card_set_id"]],
    )
    if card_type == "Follower":
        base_text = reformat_text(card["org_skill_disc"])
        evo_text = reformat_text(card["org_evo_skill_disc"])
        fields = [
            dict(name="Base", value="{atk}/{life}\n".format(**card) + base_text),
            dict(
                name="Evolved", value="{evo_atk}/{evo_life}\n".format(**card) + evo_text
            ),
        ]
    else:
        text = reformat_text(card["org_skill_disc"])
        fields = [dict(name=card_type, value=text)]
    return dict(title=title, description=description, fields=fields)


def flavor_embed(card: dict) -> dict:
    """Generate an embed for a card's flavortext."""
    card_type = card_types[card["char_type"]]
    card_set = card_sets[card["card_set_id"]]
    title = effective_card_name(card)
    description = f"Card Set: {card_set}"
    if card_type == "Follower":
        base_text = card["description"].replace("<br>", "\n")
        evo_text = card["evo_description"].replace("<br>", "\n")
        fields = [
            dict(name="Base", value=base_text),
            dict(name="Evolved", value=evo_text),
        ]
    else:
        text = card["description"].replace("<br>", "\n")
        fields = [dict(name=card_type, value=text)]
    return dict(title=title, description=description, fields=fields)


def eggsplosion_card(cards: list) -> str:
    """Return the name of a random card with 3 or less defense."""
    cards = [
        card
        for card in cards
        if card_types[card["char_type"]] == "Follower" and card["life"] <= 3
    ]
    return random.choice(cards)["card_name"]

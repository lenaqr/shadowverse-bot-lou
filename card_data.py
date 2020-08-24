import difflib
import aiohttp


_cache = None


async def update():
    global _cache
    url = "https://shadowverse-portal.com/api/v1/cards?format=json&lang=en"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            json = await response.json()
    _cache = json["data"]["cards"]


async def get() -> list:
    if _cache is None:
        await update()
    return _cache


def find(cards: list, query: str, *, num_results: int) -> list:
    if query.isdigit():
        card_id = int(query)
        return [card for card in cards if card["card_id"] == card_id]

    results = []
    query_words = query.lower().split()
    for i, card in enumerate(cards):
        card_name = card["card_name"]
        if card_name is None:
            continue
        if query.islower():
            card_name = card_name.lower()
        if query == card_name:
            is_exact = True
            match_size = len(query)
            match_cost = len(query)
        else:
            is_exact = False
            s = difflib.SequenceMatcher(str.isspace, query, card_name, autojunk=False)
            blocks = s.get_matching_blocks()
            match_size = 0
            match_cost = len(query)
            pos = 0
            for block in blocks:
                match_size += block.size
                num_unmatched_words = len(card_name[pos : block.b].split())
                if block.b == len(card_name):
                    if num_unmatched_words > 0:
                        match_cost += 1
                    if (
                        num_unmatched_words > 1
                        and pos < len(card_name)
                        and not card_name[pos].isspace()
                        and not card_name[pos] == ","
                    ):
                        match_cost += 1
                else:
                    match_cost += num_unmatched_words
                pos = block.b + block.size
            assert pos == len(card_name)
        card_id = card["card_id"]
        is_alt_or_token = card_id >= 700000000
        key = (-is_exact, -match_size / match_cost, is_alt_or_token, -card_id)
        results.append((key, i))
    results.sort()
    return [cards[i] for (_, i) in results[:num_results]]


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
rarities = {1: "Bronze", 2: "Silver", 3: "Gold", 4: "Legendary"}
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
    90000: "Token",
}


def reformat_text(text: str) -> str:
    return (
        text.replace("<br>", "\n")
        .replace("[/b][b]", "")
        .replace("[b]", "**")
        .replace("[/b]", "**")
    )


def info_embed(card: dict) -> dict:
    card_type = card_types[card["char_type"]]
    title = card["card_name"]
    description = ("{cost}pp {craft} {rarity} {card_type}\nTrait: {trait}").format(
        cost=card["cost"],
        craft=crafts[card["clan"]],
        rarity=rarities[card["rarity"]],
        card_type=card_type,
        trait=card["tribe_name"],
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
    card_type = card_types[card["char_type"]]
    card_set = card_sets[card["card_set_id"]]
    title = card["card_name"]
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

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
    10008: "Dawnbreak Nightedge",
    10009: "Brigade of the Sky",
    10010: "Omen of the Ten",
    10011: "Altersphere",
    10012: "Steel Rebellion",
    10013: "Rebirth of Glory",
    10014: "Verdant Conflict",
    10015: "Ultimate Colosseum",
    10016: "World Uprooted",
    10017: "Fortune's Hand",
    10018: "Storm Over Rivayle",
    10019: "Eternal Awakening",
    10020: "Darkness Over Vellsar",
    10021: "Renascent Chronicles",
    10022: "Dawn of Calamity",
    10023: "Omen of Storms",
    10024: "Edge of Paradise",
    10025: "Upcoming Card Set 25",
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
    70018: "Shadowverse: Champion's Battle Tie-in",
    70019: "Shadowverse: Champion's Battle",
    70020: "Granblue Fantasy Tie-in",
    70021: "Battle Pass",
    70022: "Kaguya-sama: Love Is War? Tie-in",
    70023: "The Idolmaster: Cinderella Girls Tie-in",
    70024: "Upcoming Tie-in 24",
    70025: "Upcoming Tie-in 25",
    90000: "Token",
}
formats = {
    0: "Unlimited",
    1: "Rotation",
}


_cache = None


async def _update():
    global _cache
    url = "https://shadowverse-portal.com/api/v1/cards?format=json&lang=en"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            json = await response.json()
    cards = json["data"]["cards"]

    # compute derived fields -- currently just base card set id
    cards_by_id = {card["card_id"]: card for card in cards}
    for card in cards:
        card["base_card_set_id"] = cards_by_id[card["base_card_id"]]["card_set_id"]

    _cache = cards


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
        if card["card_set_id"] == card["base_card_set_id"]:
            return card_name + " (Alt Leader)"
        elif card["card_set_id"] == 90000:
            return card_name + " (Token)"
        else:
            card_set = card_sets[card["card_set_id"]]
            return card_name + f" (Alt: {card_set})"
    return card_name


def name_match_score(card_name: str, query: str) -> float:
    """Match the card name to the given query. Return a score between 0 and 1."""
    # iterate over blocks of matching characters as returned by
    # difflib, to get
    # - "match_size", the number of matching characters
    # - "match_cost", the number of edit operations from the card name
    #   to the search query
    if query.islower():
        card_name = card_name.lower()
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
    return match_size / match_cost


def find_by_name(cards: list, query: str, *, threshold) -> list:
    """Find cards whose names match the query string."""
    results = []
    for i, card in enumerate(cards):
        card_name = card["card_name"]
        if card_name is None:
            continue
        match_score = name_match_score(card_name, query)
        if match_score >= threshold:
            card_id = card["card_id"]
            is_alt_or_token = card_id >= 700000000 or card_id != card["base_card_id"]
            key = (-match_score, is_alt_or_token, -card["card_set_id"], card_name)
            results += [(key, i)]
    results.sort()
    return [cards[i] for (key, i) in results]


def find_by_keywords(cards: list, query: list) -> list:
    """Search cards by full text and keywords."""
    results = []
    for i, card in enumerate(cards):
        card_name = effective_card_name(card)
        if card_name is None:
            continue
        fields = [
            card_name,
            "{cost}pp".format(cost=card["cost"]),
            crafts[card["clan"]],
            rarities[card["rarity"]],
            card_types[card["char_type"]],
            card["tribe_name"],
            card_sets[card["card_set_id"]],
            formats[card["format_type"]],
            card["skill_disc"],
            card["evo_skill_disc"],
            "{atk}/{life}".format(atk=card["atk"], life=card["life"]),
        ]
        is_match = True
        for query_word in query:
            word_found = False
            for field in fields:
                if (
                    query_word.lower() == "storm"
                    and field.lower() == "storm over rivayle"
                    and "rivayle" not in (q.lower() for q in query)
                ):
                    # special case: ignore "storm" in "storm over rivayle"
                    continue
                if (
                    query_word.lower() == "storm"
                    and field.lower() == "omen of storms"
                    and "omen" not in (q.lower() for q in query)
                ):
                    # special case: ignore "storm" in "omen of storms"
                    continue
                if query_word in (field.lower() if query_word.islower() else field):
                    word_found = True
                    break
            if not word_found:
                is_match = False
                break
        if is_match:
            card_id = card["card_id"]
            is_alt_or_token = card_id >= 700000000 or card_id != card["base_card_id"]
            key = (is_alt_or_token, -card["card_set_id"], card_name)
            results += [(key, i)]
    results.sort()
    return [cards[i] for (key, i) in results]


def find(cards: list, query: list, threshold=0.75) -> list:
    """Find by name or keywords."""
    name_results = find_by_name(cards, " ".join(query), threshold=threshold)
    keyword_results = find_by_keywords(cards, query)
    if len(keyword_results) >= 1:
        # Return results in the order that they appear in `name_results`, if
        # they do appear.
        result_ids = set(card["card_id"] for card in keyword_results)
        results = []
        for card in name_results + keyword_results:
            try:
                result_ids.remove(card["card_id"])
            except KeyError:
                continue
            results += [card]
        assert not result_ids
        return results
    else:
        return name_results


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
    url = "https://shadowverse-portal.com/card/" + str(card["card_id"])
    return dict(title=title, description=description, fields=fields, url=url)


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


def random_card(cards: list, eggsplosion: bool = False) -> dict:
    """Return the name of a random card."""

    if eggsplosion:
        cards = [
            card
            for card in cards
            if card_types[card["char_type"]] == "Follower" and card["life"] <= 3
        ]
    else:
        cards = [card for card in cards if card["card_id"] < 700000000]
    return random.choice(cards)

import aiohttp

import card_data


async def get(code: str) -> dict:
    """Look up a deck code."""
    async with aiohttp.ClientSession() as session:
        url = (
            "https://shadowverse-portal.com/api/v1/deck/import"
            f"?format=json&deck_code={code}"
        )
        async with session.get(url) as response:
            json = await response.json()
            h = json["data"]["hash"]

        url = (
            "https://shadowverse-portal.com/api/v1/deck"
            f"?format=json&lang=en&hash={h}"
        )
        async with session.get(url) as response:
            json = await response.json()
            deck = json["data"]["deck"]

    return {"hash": h, "deck": deck}


def embed(data: dict) -> dict:
    """Generate an embed for a deck."""
    title = card_data.crafts[data["deck"]["clan"]]

    counts = {}
    for card in data["deck"]["cards"]:
        card_name = card["card_name"]
        counts[card_name] = counts.get(card_name, 0) + 1

    description = "\n".join(
        f"{count}× {card_name}" for (card_name, count) in counts.items()
    )
    url = "https://shadowverse-portal.com/deck/" + data["hash"]
    return dict(title=title, description=description, url=url)

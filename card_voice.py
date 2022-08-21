import io
import os
import tempfile

import aiohttp

import card_data


_soundmanifest = None


async def get_soundmanifest() -> dict:
    global _soundmanifest
    if _soundmanifest is not None:
        return _soundmanifest

    res_ver = os.environ["RES_VER"]
    url = f"https://shadowverse.akamaized.net/dl/Manifest/{res_ver}/Eng/Windows/soundmanifest"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()

    ret = {}
    for line in text.splitlines():
        fields = line.split(",")
        if len(fields) < 2:
            continue
        [name, hexcode, *_] = fields

        prefix = "v/vo_"
        suffix = ".acb"
        if not name.startswith(prefix) and name.endswith(suffix):
            continue
        card_id = name[len(prefix) : -len(suffix)]

        if not card_id.isdigit():
            continue
        card_id = int(card_id)

        ret[card_id] = hexcode

    _soundmanifest = ret
    return ret


async def svgdb_get(card_id: int) -> list:
    url = f"https://svgdb.me/api/voices/{card_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            json = await response.json()

    ret = []
    for label, basenames in json.items():
        translate = {
            "plays": "play",
            "evolves": "evolve",
            "attacks": "attack",
            "deaths": "death",
        }
        label = translate.get(label, label).capitalize()
        for basename in basenames:
            en = f"https://svgdb.me/assets/audio/en/{basename}"
            jp = f"https://svgdb.me/assets/audio/jp/{basename}"
            ret.append((label, en, jp))

    return ret


async def svgdb_embed(card: dict) -> dict:
    card_id = card["card_id"]
    data = await svgdb_get(card_id)
    title = card_data.effective_card_name(card)
    description = (
        "Provided by [svgdb.me](https://svgdb.me). "
        "This bot is not affiliated with svgdb."
    )
    fields = [
        dict(name=label, value=f"[en]({en}) [jp]({jp})") for label, en, jp in data
    ]
    url = f"https://svgdb.me/cards/{card_id}"
    return dict(title=title, description=description, fields=fields, url=url)

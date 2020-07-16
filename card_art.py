import io
import os
import tempfile

import aiohttp
import PIL
import unitypack


_assetmanifest = None
_asset_cache = {}


async def get_assetmanifest() -> dict:
    global _assetmanifest
    if _assetmanifest is not None:
        return _assetmanifest

    res_ver = os.environ["RES_VER"]
    url = f"https://shadowverse.akamaized.net/dl/Manifest/{res_ver}/Eng/Windows/card_assetmanifest"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()

    ret = {}
    for line in text.splitlines():
        fields = line.split(",")
        if len(fields) < 2:
            continue
        [name, hexcode, *_] = fields

        prefix = "card_"
        suffix = ".unity3d"
        if not name.startswith(prefix) and name.endswith(suffix):
            continue
        card_id = name[len(prefix) : -len(suffix)]

        if not card_id.isdigit():
            continue
        card_id = int(card_id)

        ret[card_id] = hexcode

    _assetmanifest = ret
    return ret


async def get_asset(card_id: int, suffix: str) -> io.BytesIO:
    data = _asset_cache.get(card_id)

    if data is None:
        manifest = await get_assetmanifest()

        hexcode = manifest.get(card_id * 10)
        if hexcode is None:
            return None

        url = f"https://shadowverse.akamaized.net/dl/Resource/Eng/Windows/{hexcode}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = _asset_cache[card_id] = await response.read()

    data = io.BytesIO(data)
    data.name = ""
    bundle = unitypack.load(data)

    image = None
    for asset in bundle.assets:
        for _, obj in asset.objects.items():
            if obj.type == "Texture2D":
                d = obj.read()
                i = d.image
                if d.name.endswith(suffix) and d.width == d.height == 1024:
                    image = d.image
                    break
        if image is not None:
            break

    if image is None:
        return None

    ret = io.BytesIO()
    image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM).resize((848, 1024))
    image.save(ret, format="png")
    ret.seek(0)

    return ret

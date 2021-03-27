import io
import os
import tempfile
import random

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
    url = f"https://shadowverse.akamaized.net/dl/Manifest/{res_ver}/Eng/Windows/sleeve_assetmanifest"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()

    ret = {}
    for line in text.splitlines():
        fields = line.split(",")
        if len(fields) < 2:
            continue
        [name, hexcode, *_] = fields

        prefix = "card_sleeve_"
        suffix = ".unity3d"
        if not name.startswith(prefix) and name.endswith(suffix):
            continue
        sleeve_id = name[len(prefix) : -len(suffix)]

        if not sleeve_id.isdigit():
            continue
        sleeve_id = int(sleeve_id)

        ret[sleeve_id] = hexcode

    _assetmanifest = ret
    return ret


async def get_random() -> io.BytesIO:
    manifest = await get_assetmanifest()

    for _ in range(10):
        sleeve_id = random.choice(list(manifest.keys()))
        asset = await get_asset(sleeve_id)
        if asset is not None:
            return asset, sleeve_id
    return None


async def get_asset(sleeve_id: int) -> io.BytesIO:
    data = _asset_cache.get(sleeve_id)

    if data is None:
        manifest = await get_assetmanifest()

        hexcode = manifest.get(sleeve_id)
        if hexcode is None:
            return None

        url = f"https://shadowverse.akamaized.net/dl/Resource/Eng/Windows/{hexcode}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = _asset_cache[sleeve_id] = await response.read()

    data = io.BytesIO(data)
    data.name = ""
    bundle = unitypack.load(data)

    image = None
    for asset in bundle.assets:
        for _, obj in asset.objects.items():
            if obj.type == "Texture2D":
                d = obj.read()
                image = d.image
                break
        if image is not None:
            break

    if image is None:
        return None

    ret = io.BytesIO()
    image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM).resize((764, 1024))
    image.save(ret, format="png")
    ret.seek(0)

    return ret

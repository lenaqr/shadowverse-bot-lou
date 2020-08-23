import pytest

import card_data


@pytest.fixture
async def cards():
    return await card_data.get()


def find(cards, query, num_results):
    return [
        card["card_name"]
        for card in card_data.find(cards, query, num_results=num_results)
    ]


def test_bellr(cards):
    assert find(cards, "bellr", 5) == ["Bellringer Angel", "Shining Bellringer Angel"]


def test_medusa(cards):
    assert find(cards, "medusa", 5) == [
        "Medusa",
        "Venomfang Medusa",
        "Venomfang Medusa",
        "Sweet-Tooth Medusa",
        "Medusa's Gaze",
    ]


def test_ladica(cards):
    assert find(cards, "ladica", 5) == [
        "Ladica's Embrace",
        "Ladica, the Stoneclaw",
    ]
    assert find(cards, "ladica,", 5) == [
        "Ladica, the Stoneclaw",
    ]


def test_tetra(cards):
    assert find(cards, "tetra", 5) == [
        "Tetra's Mettle",
        "Tetra, Sapphire Rebel",
    ]


def test_mono(cards):
    assert find(cards, "mono", 5) == [
        "Mono's Resolve",
        "Mono, Garnet Rebel",
        "Mono, Garnet Rebel",
    ]


def test_resolve(cards):
    assert find(cards, "resolve", 5) == [
        "Mono's Resolve",
        "Intertwined Resolve",
        "Leonidas's Resolve",
        "Resolve of the Fallen",
    ]


def test_prophetess(cards):
    assert find(cards, "prophetess", 5) == [
        "Elf Prophetess",
        "Prophetess of Creation",
        "Teo, Prophetess of Creation",
    ]


def test_lapis(cards):
    assert find(cards, "lapis", 5) == [
        "Lapis, Glorious Seraph",
        "Lapis, Glorious Seraph",
        "Seraph Lapis, Glory Be",
    ]


def test_elana(cards):
    assert find(cards, "elana", 5) == [
        "Elana's Prayer",
        "Elana, Purest Prayer",
    ]


def test_lococo(cards):
    assert find(cards, "elana", 5) == ["Elana's Prayer", "Elana, Purest Prayer"]


def test_robomi(cards):
    assert find(cards, "robomi", 5) == ["Go, Go, Robomi!", "Robomi, Steel Warrior"]


def test_alyaska(cards):
    assert find(cards, "alyaska", 5) == [
        "Alyaska, War Hawker",
        "Alyaska, Master Dealer",
    ]


def test_runie(cards):
    assert find(cards, "runie", 5) == [
        "Runie, Resolute Diviner",
        "Runie, Destiny's Bard",
    ]


def test_neph(cards):
    assert find(cards, "neph", 5) == [
        "Nephthys",
        "Nephthys",
        "Nephthys, Goddess of Amenta",
    ]


def test_arriet(cards):
    assert find(cards, "arriet", 5) == ["Luxblade Arriet", "Arriet, Soothing Harpist"]


def test_otohime(cards):
    assert find(cards, "otohime", 5) == [
        "Sea Queen Otohime",
        "Sea Queen Otohime",
        "Dragon Empress Otohime",
        "Otohime's Bodyguard",
        "Otohime's Vanguard",
    ]


def test_ines(cards):
    assert find(cards, "ines", 5) == ["Ines, Maiden of Clouds"]


def test_ameth(cards):
    assert find(cards, "ameth", 5) == [
        "Amethyst Giant",
        "Ameth, Dream Emissary",
        "Aenea, Amethyst Rebel",
        "Aenea, Amethyst Rebel",
    ]


def test_hades(cards):
    assert find(cards, "hades", 5) == [
        "Cerberus, Hound of Hades",
        "Hades, Father of Purgatory",
        "Hades, Father of Purgatory",
    ]


def test_steadfast(cards):
    assert find(cards, "steadfast", 5) == ["Steadfast Angel", "Steadfast Samurai"]


def test_stalwart(cards):
    assert find(cards, "stalwart", 5) == [
        "Stalwart Featherfolk",
        "Aquascale Stalwart",
        "Jeno, Levin Stalwart",
        "Nicholas, Stalwart Inventor",
    ]


def test_shin(cards):
    assert find(cards, "shin", 5) == [
        "Shin, Lawful Light",
        "Shining Bellringer Angel",
        "Shinobu, Mausoleum Medium",
        "Shin, Chaotic Darkness",
    ]


def test_lina(cards):
    assert find(cards, "lina", 5) == ["Lina & Lena, Twin Souls"]


def test_ra(cards):
    assert find(cards, "ra", 5) == [
        "Rapunzel",
        "Rahab",
        "Meowskers's Raid",
        "Rapier Master",
        "Flame Rat",
    ]


def test_shion(cards):
    assert find(cards, "shion", 5) == [
        "Shion, Mercurial Aegis",
    ]


def test_elf_queen(cards):
    assert find(cards, "elf queen abundant life", 5) == ["Elf Queen of Abundant Life"]


def test_rebel_fate(cards):
    assert find(cards, "rebel fate", 5) == ["Rebel Against Fate"]


def test_xi(cards):
    assert find(cards, "XI.", 5) == ["XI. Erntz, Justice"]


def test_dragonflute(cards):
    assert find(cards, "dragonflute", 5) == []


def test_dragonkeeper(cards):
    assert find(cards, "prime dragonkeeper", 5) == []


def test_demon_lord(cards):
    assert find(cards, "demon lord", 5) == []


def test_ignorance(cards):
    assert find(cards, "rite of ignorance", 5) == []


def test_demon_eachtar(cards):
    assert find(cards, "demon eachtar", 5) == ["Demonlord Eachtar "]


def test_heavens_gate(cards):
    assert find(cards, "heaven’s gate", 5) == ["Heaven's Gate"]
    assert find(cards, "heavens gate", 5) == []


def test_themis_decree(cards):
    assert find(cards, "themis decree", 5) == ["Themis's Decree"]


def test_tetra_met(cards):
    assert find(cards, "tetra met", 5) == ["Tetra's Mettle"]


def test_dis_damnation(cards):
    assert find(cards, "dis damnation", 5) == ["Dis's Damnation"]


def test_death_mist(cards):
    assert find(cards, "death mist", 5) == ["Death's Mistress"]


def test_arcus_ghostly(cards):
    assert find(cards, "arcus ghostly", 5) == ["Arcus, Ghostly Manager"]


def test_awaken_gaia(cards):
    assert find(cards, "awaken gaia", 5) == ["Awakened Gaia"]


def test_liberte(cards):
    assert find(cards, "liberte", 5) == []


def test_terminus_weap(cards):
    assert find(cards, "terminus weap", 5) == []


def test_eggsplotion(cards):
    assert find(cards, "eggsplotion", 5) == []


def test_nepthys(cards):
    assert find(cards, "nepthys", 5) == []


def test_weilder(cards):
    assert find(cards, "chaos weilder", 5) == []


def test_lucoco(cards):
    assert find(cards, "lucoco", 5) == []


def test_weaponary(cards):
    assert find(cards, "forged weaponary", 5) == []


def test_vortex(cards):
    assert find(cards, "vortex colony", 5) == []


def test_radient(cards):
    assert find(cards, "ra, radient", 5) == []


def test_shudderwock(cards):
    assert find(cards, "shudderwock", 5) == []


def test_ironstinger(cards):
    assert find(cards, "ironstinger", 5) == []


def test_nicolas(cards):
    assert find(cards, "nicolas", 5) == []


def test_fantasmal(cards):
    assert find(cards, "fantasmal fairy", 5) == []


def test_absorbtion(cards):
    assert find(cards, "mystic absorbtion", 5) == []


def test_falconeer(cards):
    assert find(cards, "storied falconeer", 5) == []

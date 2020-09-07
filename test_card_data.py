import pytest

import card_data


@pytest.fixture
async def cards():
    return await card_data.get()


def find(cards, query):
    return [
        card_data.effective_card_name(card) for card in card_data.find(cards, query)
    ]


def test_bellr(cards):
    assert find(cards, "bellr")[:1] == [
        "Bellringer Angel",
    ]


def test_medusa(cards):
    assert find(cards, "medusa")[:6] == [
        "Medusa",
        "Medusa, Evil-Eyed Serpent",
        "Sweet-Tooth Medusa",
        "Venomfang Medusa",
        "Medusa's Gaze",
        "Medusiana",
    ]


def test_ladica(cards):
    assert find(cards, "ladica")[:2] == [
        "Ladica, the Stoneclaw",
        "Ladica's Embrace",
    ]


def test_tetra(cards):
    assert find(cards, "tetra")[:2] == [
        "Tetra, Sapphire Rebel",
        "Tetra's Mettle",
    ]


def test_mono(cards):
    assert find(cards, "mono")[:1] == [
        "Mono, Garnet Rebel",
    ]
    assert find(cards, "mono's")[:1] == [
        "Mono's Resolve",
    ]


def test_resolve(cards):
    assert find(cards, "resolve")[:5] == [
        "Resolve of the Fallen",
        "Intertwined Resolve",
        "Mono's Resolve",
        "Leonidas's Resolve",
        "Gelt, Resolute Knight",
    ]


def test_prophetess(cards):
    assert find(cards, "prophetess")[:5] == [
        "Prophetess of Creation",
        "Elf Prophetess",
        "Teo, Prophetess of Creation (Alt: Omen of the Ten)",
        "Protectoress",
        "Prism Priestess",
    ]


def test_lapis(cards):
    assert find(cards, "lapis")[:3] == [
        "Lapis, Glorious Seraph",
        "Lapis, Glorious Seraph (Alt: Omen of the Ten)",
        "Seraph Lapis, Glory Be",
    ]


def test_elana(cards):
    assert find(cards, "elana")[:2] == [
        "Elana, Purest Prayer",
        "Elana's Prayer",
    ]


def test_lococo(cards):
    assert find(cards, "lococo")[:2] == [
        "Lococo, Little Puppeteer",
        "Lococo's Teddy Bear",
    ]


def test_robomi(cards):
    assert find(cards, "robomi")[:3] == [
        "Robomi, Steel Warrior",
        "Robozombie",
        "Go, Go, Robomi!",
    ]


def test_alyaska(cards):
    assert find(cards, "alyaska")[:2] == [
        "Alyaska, War Hawker",
        "Alyaska, Master Dealer",
    ]


def test_runie(cards):
    assert find(cards, "runie")[:2] == [
        "Runie, Resolute Diviner",
        "Runie, Destiny's Bard",
    ]


def test_neph(cards):
    assert find(cards, "neph")[:3] == [
        "Nephthys",
        "Nephthys, Goddess of Amenta",
        "Nephthys (Alt: Prebuilt Decks 2)",
    ]
    assert find(cards, "neph,")[:1] == [
        "Nephthys, Goddess of Amenta",
    ]
    assert find(cards, "neph alt")[:1] == [
        "Nephthys (Alt: Prebuilt Decks 2)",
    ]


def test_arriet(cards):
    assert find(cards, "arriet")[:2] == [
        "Luxblade Arriet",
        "Arriet, Soothing Harpist",
    ]
    assert find(cards, "arriet,")[:1] == [
        "Arriet, Soothing Harpist",
    ]


def test_otohime(cards):
    assert find(cards, "otohime")[:5] == [
        "Dragon Empress Otohime",
        "Sea Queen Otohime",
        "Otohime's Vanguard",
        "Otohime's Bodyguard",
        "Sea Queen Otohime (Alt: Prebuilt Decks 1)",
    ]


def test_ines(cards):
    assert find(cards, "ines")[:1] == [
        "Ines, Maiden of Clouds",
    ]


def test_ameth(cards):
    assert find(cards, "ameth")[:2] == [
        "Ameth, Dream Emissary",
        "Amethyst Giant",
    ]


def test_hades(cards):
    assert find(cards, "hades")[:1] == [
        "Hades, Father of Purgatory",
    ]


def test_steadfast(cards):
    assert find(cards, "steadfast")[:2] == [
        "Steadfast Samurai",
        "Steadfast Angel",
    ]


def test_stalwart(cards):
    assert find(cards, "stalwart")[:4] == [
        "Stalwart Featherfolk",
        "Aquascale Stalwart",
        "Jeno, Levin Stalwart",
        "Nicholas, Stalwart Inventor",
    ]


def test_shin(cards):
    assert find(cards, "shin")[:3] == [
        "Shin, Lawful Light",
        "Shin, Chaotic Darkness",
        "Shinobu, Mausoleum Medium",
    ]


def test_lina(cards):
    assert find(cards, "lina")[:1] == [
        "Lina & Lena, Twin Souls",
    ]


def test_ra(cards):
    assert find(cards, "ra")[:1] == [
        "Ra, Radiance Incarnate",
    ]


def test_shion(cards):
    assert find(cards, "shion")[:1] == [
        "Shion, Mercurial Aegis",
    ]


def test_elf_queen(cards):
    assert find(cards, "elf queen abundant life")[:1] == ["Elf Queen of Abundant Life"]


def test_rebel_fate(cards):
    assert find(cards, "rebel fate")[:1] == ["Rebel Against Fate"]


def test_xi(cards):
    assert find(cards, "XI.")[:1] == ["XI. Erntz, Justice"]


def test_dragonflute(cards):
    assert find(cards, "dragonflute")[:1] == ["Dragonsong Flute"]


def test_dragonkeeper(cards):
    assert find(cards, "prime dragonkeeper")[:1] == ["Prime Dragon Keeper"]


def test_demon_lord(cards):
    assert find(cards, "demon lord")[:1] == ["Demonlord Eachtar "]


def test_ignorance(cards):
    assert find(cards, "rite of ignorance")[:1] == ["Rite of the Ignorant"]


def test_demon_eachtar(cards):
    assert find(cards, "demon eachtar")[:1] == ["Demonlord Eachtar "]


def test_heavens_gate(cards):
    assert find(cards, "heaven’s gate")[:1] == ["Heaven's Gate"]
    assert find(cards, "heavens gate")[:1] == ["Heaven's Gate"]


def test_themis_decree(cards):
    assert find(cards, "themis decree")[:1] == ["Themis's Decree"]


def test_tetra_met(cards):
    assert find(cards, "tetra met")[:1] == ["Tetra's Mettle"]


def test_dis_damnation(cards):
    assert find(cards, "dis damnation")[:1] == ["Dis's Damnation"]


def test_death_mist(cards):
    assert find(cards, "death mist")[:1] == ["Death's Mistress"]


def test_arcus_ghostly(cards):
    assert find(cards, "arcus ghostly")[:1] == ["Arcus, Ghostly Manager"]


def test_awaken_gaia(cards):
    assert find(cards, "awaken gaia")[:1] == ["Awakened Gaia"]


def test_liberte(cards):
    assert find(cards, "liberte")[:1] == ["Liberté, Werewolf Pup"]


def test_terminus_weap(cards):
    assert find(cards, "terminus weap")[:1] == ["Exterminus Weapon"]


def test_eggsplotion(cards):
    assert find(cards, "eggsplotion")[:1] == ["Eggsplosion"]


def test_nepthys(cards):
    assert find(cards, "nepthys")[:1] == ["Nephthys"]


def test_weilder(cards):
    assert find(cards, "chaos weilder")[:1] == ["Chaos Wielder"]


def test_weaponary(cards):
    assert find(cards, "forged weaponary")[:1] == ["Forge Weaponry"]


def test_vortex(cards):
    assert find(cards, "vortex colony")[:1] == ["Vertex Colony"]


def test_radient(cards):
    assert find(cards, "ra, radient")[:1] == ["Ra, Radiance Incarnate"]


def test_ironstinger(cards):
    assert find(cards, "ironstinger")[:1] == ["Ironsting Archaeologist"]


def test_nicolas(cards):
    assert find(cards, "nicolas")[:2] == [
        "Nicholas, Stalwart Inventor",
        "Nicola, Forbidden Strength",
    ]


def test_fantasmal(cards):
    assert find(cards, "fantasmal fairy")[:1] == ["Phantasmal Fairy Dragon"]


def test_absorbtion(cards):
    assert find(cards, "mystic absorbtion")[:1] == ["Mystic Absorption"]


def test_falconeer(cards):
    assert find(cards, "storied falconeer")[:1] == ["Storied Falconer"]

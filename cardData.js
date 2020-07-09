const fetch = require("node-fetch");

let cache = null;

async function update() {
  console.log("Fetching card data...");
  let res = await fetch(
    "https://shadowverse-portal.com/api/v1/cards?format=json&lang=en"
  );
  let json = await res.json();
  console.log("Got card data");
  cache = json.data.cards;
  return cache;
}

async function get() {
  if (cache === null) {
    return update();
  } else {
    return cache;
  }
}

function find(cards, queryWords, numResults) {
  let results = [];
  queryWords = queryWords.map(word => word.toLowerCase());
  cards.forEach(card => {
    if (card.card_name === null) return;
    let nameWords = card.card_name.toLowerCase().split(/ +/);
    let score = 0;
    let isMatch = queryWords.every(queryWord => {
      if (nameWords.includes(queryWord)) {
        score += 3;
        return true;
      }
      if (nameWords.some(nameWord => nameWord.startsWith(queryWord))) {
        score += 1;
        return true;
      }
      return false;
    });
    score /= nameWords.length;
    if (isMatch) {
      results.push({ card, score });
    }
  });
  results = results.sort((a, b) => b.score - a.score).slice(0, numResults);
  return results.map(r => r.card);
}

const crafts = [
  "Neutral",
  "Forestcraft",
  "Swordcraft",
  "Runecraft",
  "Dragoncraft",
  "Shadowcraft",
  "Bloodcraft",
  "Havencraft",
  "Portalcraft"
];

const rarities = ["Bronze", "Silver", "Gold", "Legendary"];

const cardtypes = [
  "Follower",
  "Amulet", // permanent
  "Amulet", // countdown
  "Spell"
];

const cardsets = {
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
  90000: "Token"
};

function fillEmbed(embed, card) {
  let cost = card.cost;
  let craft = crafts[card.clan];
  let rarity = rarities[card.rarity - 1];
  let cardtype = cardtypes[card.char_type - 1];
  let trait = card.tribe_name;
  let cardset = cardsets[card.card_set_id];
  let description = [
    `${cost}pp ${craft} ${rarity} ${cardtype}`,
    `Trait: ${trait}`,
    `Card Set: ${cardset}`
  ].join("\n");
  embed.setTitle(card.card_name);
  embed.setDescription(description);
  if (cardtype === "Follower") {
    let text = card.skill_disc.replace(/<br>/g, "\n");
    let evo_text = card.evo_skill_disc.replace(/<br>/g, "\n");
    embed.addField("Base", `${card.atk}/${card.life}\n${text}`);
    embed.addField("Evolved", `${card.evo_atk}/${card.evo_life}\n${evo_text}`);
  } else {
    let text = card.skill_disc.replace(/<br>/g, "\n");
    embed.addField(cardtype, text);
  }
}

module.exports = { update, get, find, fillEmbed };

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

function find(cards, queryWords) {
  queryWords = queryWords.map(word => word.toLowerCase());
  let best = null;
  let bestScore = 0;
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
    if (isMatch && score > bestScore) {
      best = card;
      bestScore = score;
    }
  });
  return best;
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

function fillEmbed(embed, card) {
  let cost = card.cost;
  let craft = crafts[card.clan];
  let rarity = rarities[card.rarity - 1];
  let cardtype = cardtypes[card.char_type - 1];
  let trait = card.tribe_name;
  embed.setTitle(card.card_name);
  embed.setDescription(`${cost}pp ${craft} ${rarity} ${cardtype}\n${trait}`);
  if (cardtype === "Follower") {
    let text = card.skill_disc.replace(/<br>/g, "\n");
    let evo_text = card.evo_skill_disc.replace(/<br>/g, "\n");
    embed.addField("Base", `${card.atk}/${card.life}\n${text}`);
    embed.addField("Evolved", `${card.evo_atk}/${card.evo_life}\n${evo_text}`);
  } else {
    let text = card.skill_disc.replace(/<br>/g, "\n");
    embed.addField("Base", text);
  }
}

module.exports = { update, get, find, fillEmbed };

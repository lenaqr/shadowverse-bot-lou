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

module.exports = { update, get };

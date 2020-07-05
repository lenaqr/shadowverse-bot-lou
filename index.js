const Discord = require("discord.js");
const cardData = require("./cardData.js");

const prefix = process.env.BOT_PREFIX;
const client = new Discord.Client();

client.once("ready", () => {
  console.log(`Logged in as ${client.user.tag}`);
});

client.on("message", async message => {
  if (!message.content.startsWith(prefix) || message.author.bot) return;

  const args = message.content.slice(prefix.length).split(/ +/);
  const command = args.shift().toLowerCase();

  if (command === "ping") {
    await message.channel.send("Pong.");
  } else if (command === "fetch") {
    await message.channel.send("Fetching card data...");
    let cards = await cardData.update();
    await message.channel.send(`Got ${cards.length} cards.`);
  } else if (command === "card") {
    let queryWords = args.map(arg => arg.toLowerCase());
    let cards = await cardData.get();
    let matches = cards.filter(card => {
      if (card.card_name === null) return false;
      let nameWords = card.card_name.toLowerCase().split(/ +/);
      return queryWords.every(queryWord =>
        nameWords.some(nameWord => nameWord.startsWith(queryWord))
      );
    });
    await message.channel.send(
      `Found ${matches.length} cards matching "${queryWords}".`
    );
  }
});

client.login(process.env.DISCORD_TOKEN);

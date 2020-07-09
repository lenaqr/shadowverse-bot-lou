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
  } else if (command == "invite") {
    let link = await client.generateInvite(["SEND_MESSAGES", "EMBED_LINKS"]);
    await message.channel.send(`Invite me to your server: <${link}>`);
  } else if (command === "fetch") {
    await message.channel.send("Fetching card data...");
    let cards = await cardData.update();
    await message.channel.send(`Got ${cards.length} cards.`);
  } else if (command === "card") {
    let cards = await cardData.get();
    let results = cardData.find(cards, args, 1);
    if (results.length === 0) {
      await message.channel.send(`No cards matching "${args.join(" ")}".`);
    } else {
      let result = results[0];
      console.log(result);
      let embed = new Discord.MessageEmbed();
      cardData.fillEmbed(embed, result);
      await message.channel.send(embed);
    }
  } else if (command === "cards") {
    let cards = await cardData.get();
    let results = cardData.find(cards, args, 10);
    if (results.length === 0) {
      await message.channel.send(`No cards matching "${args.join(" ")}".`);
    } else {
      results = results.map(card => `${card.card_id}: ${card.card_name}`);
      await message.channel.send(results.join("\n"));
    }
  }
});

client.login(process.env.DISCORD_TOKEN);

import discord
import json
import requests
import wikipedia
import os

print("Starting bot...")

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
PLANTNET_TOKEN = os.environ.get('PLANTNET_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def plant_finder(url):
    img = requests.get(url).content
    api_endpoint = f"https://my-api.plantnet.org/v2/identify/all?api-key={PLANTNET_TOKEN}"

    data = {"organs": ["leaf"]}

    files = [("images", img)]

    req = requests.Request("POST", url=api_endpoint, files=files, data=data)
    prepared = req.prepare()
    s = requests.Session()
    response = s.send(prepared)

    try:
        results = json.loads(response.text)["results"][0]
    except:
        raise ValueError("No results found")

    commonNames = results["species"]["commonNames"]
    family = results["species"]["family"]["scientificNameWithoutAuthor"]
    scientificName = results["species"]["scientificNameWithoutAuthor"]

    commonNamesString = ""
    if len(commonNames) > 1:
        for name in commonNames:
            commonNamesString += f"  • {name}\n"

    elif len(commonNames) == 1:
        commonNamesString = f"  • {commonNames[0]}"

    return commonNamesString, family, scientificName


def format_text(url):
    commonNamesString, family, scientificName = plant_finder(url)
    embed = discord.Embed(title=scientificName, description=wikipedia.summary(
        scientificName, sentences=1), color=0x246815)
    embed.set_thumbnail(url=url)
    embed.add_field(name="Family", value=wikipedia.summary(
        family, sentences=1), inline=True)
    embed.add_field(name="Common Names:", value=commonNamesString, inline=True)

    return embed


@client.event
async def on_ready():
    print(f'connected as: {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!hewo'):
        await message.channel.send('Hello!')

    if message.content.startswith('!find'):
        if message.attachments:
            url = message.attachments[0].url

            msg = await message.channel.send(f"Solving...", reference=message)
            try:
                embed = format_text(url)
                await msg.edit(content="", embed=embed)
            except ValueError:
                await msg.edit(content="There was an error solving the image. Please try again.")
        else:
            await message.channel.send('Nothing to find here...')

client.run(DISCORD_TOKEN)

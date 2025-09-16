import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests
import urllib.parse
import html

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

URL = "https://okizeme.gg/api/"

handler = logging.FileHandler(filename='discord.log', encoding='UTF-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='+', intents=intents)


# this is to talk to the bot directly, instead of handling an event


@bot.command()
async def move(ctx, *, msg):
    msg = msg.split(" ", 1)
    print(msg)
    if len(msg) != 2:
        await ctx.send("Invalid Command")
    character = msg[0]
    command_name = msg[1]
    data = get_move(character, command_name)

    # Clean up notes (decode HTML entities + strip tags)
    notes = html.unescape(data.get("notes") or "")
    notes = notes.replace("<div class=\"plainlist\">", "").replace("</div>", "")
    notes = notes.replace("\n", "\n")  # keep bullet points readable

    # Build embed
    embed = discord.Embed(
        title=f"🥊 {data['name']}",
        description=f"**Command:** `{data['command']}`",
        color=discord.Color.blue()
    )

    embed.add_field(name="⚡ Startup", value=data["startup"] or "—", inline=True)
    embed.add_field(name="🛡️ On Block", value=data["block"] or "—", inline=True)
    embed.add_field(name="💥 On Hit", value=data["hit"] or "—", inline=True)
    
    # Add hit level if available (always uppercase)
    if data.get("hitLevel"):
        embed.add_field(name="🎯 Hit Level", value=data["hitLevel"].upper(), inline=True)

    if notes.strip():
        embed.add_field(name="📝 Notes", value=notes, inline=False)

    if data.get("video"):
        embed.add_field(name="🎥 Video", value=f"[▶ Watch here]({data['video']})", inline=False)

    embed.set_footer(text=f"{character} • okizeme.gg")

    await ctx.send(embed=embed)
    await ctx.send(data["video"])


def get_move(character: str, command_name: str):
    data = {}

    print(f"Sending Request to {URL + character.lower()}")
    response = requests.get(URL + character.lower())
    response.raise_for_status()

    movelist = response.json()

    for command in movelist:
        if command['command'].lower() == command_name.lower():
            data['name'] = command['name']
            data['command'] = command['command']
            data['hitLevel'] = command['hitLevel']
            data['startup'] = command['startup']
            data['block'] = command['block']
            data['hit'] = command['hit']
            data['notes'] = command['notes']
            encoded_name = urllib.parse.quote(command["command"])
            data['video'] = f"https://okizeme.b-cdn.net/{character.lower()}/{encoded_name}.mp4"

    return data


bot.run(token, log_handler=handler, log_level=logging.DEBUG)

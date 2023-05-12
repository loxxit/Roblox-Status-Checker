import os
try:
    import requests
    import time
    import json
    import logging
    from discord import Status
    import discord
    from rgbprint import gradient_print, Color
    from discord.ext import commands, tasks
    import asyncio
except ModuleNotFoundError as e:
    print(f"Missing module: {e.name}")
    with open("requirements.txt") as f:
        modules = f.read().splitlines()
        os.system(f"pip install {' '.join(modules)}")

logging.basicConfig(level=logging.INFO)
logging.getLogger('discord.client').setLevel(logging.WARNING)
logging.getLogger('discord.gateway').setLevel(logging.WARNING)

os.system("color c")

with open("config.json") as f:
    config = json.load(f)

DISCORD_TOKEN = config["token"]
DISCORD_CHANNEL_ID = config["id"]

intents = discord.Intents.default()
client = discord.Client(intents=intents)

ROBLOX_CLIENT_VERSION_API = "https://setup.rbxcdn.com/version"

current_version = config["current_version"]
last_checked = None
task = None
current_task = None

@tasks.loop(seconds=1)
async def check_for_updates():
    global current_version, last_checked, task
    response = requests.get(ROBLOX_CLIENT_VERSION_API)
    new_version = response.text.strip()
    if new_version != current_version:
        config["current_version"] = new_version
        task = "new"
        embed = discord.Embed(title='Roblox Updated', color=0xFF0000)
        embed.add_field(name='', value=f'**{new_version}** Old Version: **{current_version}**', inline=False)
        embed.set_footer(text=f'Last checked: {time.strftime("%m/%d/%Y %I:%M %p")}')
        last_checked = time.time()

        
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        current_version = new_version

        channel = client.get_channel(DISCORD_CHANNEL_ID)
        task = "embed"
        await channel.send(embed=embed)

        gradient_print(f"Update found: {new_version} - Version updated in config.json", start_color=Color.light_green, end_color=Color.pale_turquoise)
    else:
        if task != "checking":
            task = "checking"
            gradient_print("No updates found - Checking for updates.", start_color=Color.purple, end_color=Color.khaki)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=config["activity"]), status=config["status"])
    await check_for_updates.start()

client.run(DISCORD_TOKEN)

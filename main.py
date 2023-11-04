import os
try:
    import discord
    import time
    import json
    import requests
    from discord.ext import tasks, commands
    ROBLOX_CLIENT_VERSION_API = "https://setup.rbxcdn.com/version"
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        bot_token = config.get('bot_token')
        if not bot_token:
            raise ValueError("Bot token is not found in config.json")
    except FileNotFoundError:
        raise FileNotFoundError("config.json file not found")

    secs = 5
    with open('config.json', 'r') as config_file:
            config = json.load(config_file)
    secs = config.get('secs')
    print(f"will check every {secs} secs")
    url = "https://www.roblox.com/home"
    url2 = "https://status.roblox.com/"
    channel_id = ""
    with open('config.json', 'r') as config_file:
            config = json.load(config_file)
    channel_id = config.get('channel_id')
    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False
    bot = commands.Bot(command_prefix="px-", intents=intents)

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user.name}')
        channel = bot.get_channel(channel_id)
        activity = discord.Streaming(name="Shinsenkyo || Loxxit",url="https://github.com/loxxit")
        messages = []

        async for message in channel.history(limit=10):
            messages.append(message)

        bot_message_exists = any(message.author == bot.user for message in messages)

        if not bot_message_exists:
            await channel.send("No bot message found. Sending a new message.")
            update_message.start()

        await bot.change_presence(activity=activity, status=discord.Status.do_not_disturb)

        if bot_message_exists:
            update_message.start()
    @tasks.loop(seconds=secs)
    async def update_message():
        channel = bot.get_channel(channel_id)
        try:
            response = requests.get(url)
            response2 = requests.get(url2)
            response = requests.get(ROBLOX_CLIENT_VERSION_API)
            new_version = response.text.strip()
            print("checking...")
            if response.status_code == 200:       
                if "Active Incident" in response2.text:
                    print("200 but sd/ai")
                    message = "The website is up and running (Status Code 200) [Active Incident]"
                    color = 0xFFA500 
                else:
                    print("succes status two hundred")
                    message = "The website is up and running (Status Code 200)"
                    color = 0x00FF00 
            elif response.status_code == 503:
                print("succes status 503 SU")
                message = "SU (Service **Unavailable**)"
                color = 0xFF0000
            else:
                print(f"succes status {response.status_code}")
                message = f"Status Code: **{response.status_code}**"
                color = 0x000000 

            embed = discord.Embed(title=f"", description=message, color=color)
            last_updated = time.strftime("%d.%m.%Y %H:%M (GMT+3)", time.localtime())
            embed.set_footer(text=f"Last Updated: {last_updated}")
            embed.set_author(name="Roblox Status",url="https://status.roblox.com/",icon_url="https://devforum-uploads.s3.dualstack.us-east-2.amazonaws.com/uploads/original/4X/0/e/e/0eeeb19633422b1241f4306419a0f15f39d58de9.png")
            embed.add_field(name="Client Version",value=new_version,inline=True)
            
            if response.status_code == 503:
                embed.add_field(name="Roblox Status",value="**503**, **SU**",inline=True)
            elif response.status_code == 200:
                if "Active Incident" in response2.text:
                    embed.add_field(name="Roblox Status",value="200, Active Incident",inline=True)
                else:
                    embed.add_field(name="Roblox Status",value="200",inline=True)
            else:
                    embed.add_field(name="Roblox Status",value=f"{response.status_code}",inline=True)
            async for message in channel.history(limit=10):
                if message.author == bot.user:
                    await message.edit(content="", embed=embed)
                    break

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    bot.run(bot_token)
except ModuleNotFoundError as e:
    print(f"Missing module: {e.name}")
    with open("requirements.txt") as f:
        modules = f.read().splitlines()
        os.system(f"pip install {' '.join(modules)}")

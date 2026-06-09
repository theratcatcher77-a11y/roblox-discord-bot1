import os
import aiohttp
import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv

load_dotenv()

# VARIABLES AND SHIT
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "1499530895311241307"))
ROBLOX_USERNAME = "iIovemycars"
CHECK_SECONDS = int(os.getenv("CHECK_SECONDS", 60))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
num = 0
was_online = 0
roblox_user_id = None

# ROBLOX API SHIT
async def get_presence(user_id):
    url = "https://presence.roblox.com/v1/presence/users"

    try:
        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                url,
                json={"userIds": [user_id]}
            ) as response:

                data = await response.json()

        # Roblox API failed
        if "userPresences" not in data:
            print("Bad Roblox API response:", data)
            return 0

        return data["userPresences"][0]["userPresenceType"]

    except Exception as e:
        print("Presence Error:", e)
        return 0


# BOT CONTROL
@bot.event
async def on_ready():
    global roblox_user_id

    print(f"Logged in as {bot.user}")
    
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Bot is working!")
    
    roblox_user_id = 2459564462

    if not check_roblox_status.is_running():
        check_roblox_status.change_interval(seconds=CHECK_SECONDS)
        check_roblox_status.start()

# DA LOOP 
@tasks.loop(seconds=CHECK_SECONDS)
async def check_roblox_status():
    global was_online, num

    channel = bot.get_channel(CHANNEL_ID)
    status = await get_presence(roblox_user_id)
    
    num += 1
    print(f"[{num}] Status: {status}")
    
    status_text = {
        0: "🔴 Offline",
        1: "🟢 Online",
        2: "🎮 In Game",
        3: "🛠️ Studio"
    }.get(status, "Unknown")

    await bot.change_presence(
        activity=discord.Game(name=f"{ROBLOX_USERNAME}: {status_text} | Check #{num}")
    )
    
    # ONLINE
    if status == 1 and was_online == 0:
        try:
            await channel.send(f"🔵 @everyone **{ROBLOX_USERNAME} is online!**")
        except Exception as e:
            print("Error:", e)

    # JOINED A GAME
    elif status == 2 and was_online != 2:
        try:
            await channel.send(f"🟢 @everyone **{ROBLOX_USERNAME} joined a game!**")
        except Exception as e:
            print("Error:", e)

    # LEFT A GAME
    elif status == 1 and was_online == 2:
        try:
            await channel.send(f"🟠 @everyone **{ROBLOX_USERNAME} left the game.**")
        except Exception as e:
            print("Error:", e)
    
    
    # OFFLINE
    elif status == 0 and was_online != 0:
        try:
            await channel.send(f"🔴 @everyone **{ROBLOX_USERNAME} went offline.**")
        except Exception as e:
            print("Error:", e)

    
    was_online = status


bot.run(TOKEN)

import discord
from discord.ext import commands
from lobby import game_lobby
import dotenv
import os

dotenv.load_dotenv()

disc_token = os.getenv("DISCORD_BOT_TOKEN")
channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))

intents = discord.Intents.default()
intents.members = True  # Required to access the list of members in a channel
intents.voice_states = True  # Required to get voice channel info
intents.message_content = True

# Set up the bot
bot = commands.Bot(command_prefix="!", intents=intents)

lobby = game_lobby()

print("Bot is running")

available_gamemodes = ["melee", "ranged", "fighter", "mage", "assassin", "marksman", "tank", "support"]

@bot.check
async def globally_check_channel(ctx):
    return ctx.channel.id == channel_id


# Register a player with a gametag and store it in a database
@bot.command(name="reg")
async def register_player(ctx, gametag, tagline):
    discord_id = (
        ctx.author.id
    )  # Get the Discord ID of the person who executed the command
    discord_id = str(discord_id)

    # Register in database
    success = lobby.register_player(
        discord_id, gametag, tagline
    ) 

    if success:
        await ctx.send(f"{ctx.author.name} has been registered as {gametag}#{tagline}.")
    else:
        await ctx.send(
            f"Could not find the universal Riot ID of {gametag}#{tagline}. Control that both the name and tagline are correct."
        )


# Start a game and collect all members from the same voice channel
@bot.command(name="start")
async def start_game(ctx, gamemode = "melee"):
    gamemode = gamemode.lower() 
    if gamemode not in available_gamemodes:
        await ctx.send(f"Gamemode {gamemode} is not available. Available gamemodes: {available_gamemodes}")
        return
    
    voice_state = ctx.author.voice #Get voice channel of command author
    
    # Check if the author is in a voice channel
    if voice_state is None or voice_state.channel is None:
        await ctx.send("You are not in a voice channel.")
        return

    voice_channel = voice_state.channel
    members = voice_channel.members  # Get all members in the voice channel

    if not members:
        await ctx.send("No other members in the voice channel.")
        return

    discord_ids = [str(member.id) for member in members]  # Collect all Discord IDs
    status, gameinfo = lobby.start(discord_ids, gamemode)
    if status == True:

        # Send a message back with the IDs of all players in the voice channel
        await ctx.send(gameinfo)
    else:
        msg = "Not all players are registerd. Unregistered players: \n"
        for id in gameinfo:
            d_id = int(id)
            user = await bot.fetch_user(d_id)
            msg += f"{user.name} \n"
        await ctx.send(msg)


# Ban a champion
@bot.command(name="b")
async def ban_champ(ctx, champ):
    success = lobby.ban_champ(champ)
    if success:
        await ctx.send(f"{champ} has been banned.")
    else:
        await ctx.send(f"{champ} is already banned.")

# Unban a champion
@bot.command(name="ub")
async def unban_champ(ctx, champ):
    success = lobby.unban_champ(champ)
    if success:
        await ctx.send(f"{champ} has been unbanned.")
    else:
        await ctx.send(f"{champ} is not banned.")

# List all banned champions
@bot.command(name="lb")
async def list_banned_champs(ctx):
    banned_champs = lobby.list_banned_champs()
    if banned_champs:
        champ_list = "\n".join(banned_champs)
        await ctx.send(f"Banned champions:\n{champ_list}")
    else:
        await ctx.send("No champions are banned.")

#List all available gamemodes
@bot.command(name="modes")
async def list_gamemodes(ctx):
    modes = ", ".join(available_gamemodes)
    await ctx.send(f"Available gamemodes: {modes}")

# List all available commands
@bot.command(name="commands")
async def available_commands(ctx):
    commands = [
        "!reg <gamertag> <tagline>: Register a player with a gamertag. Ex: !reg Skutlis EUW",
        "!start <gamemode>: Start a game with all members in the voice channel (default = melee). Ex: !start support",
        "!modes: List all available gamemodes.",
        "!lc <gamemode>: List all champions available for a specific gamemode. Ex: !lc support",
        "!b <champ>: Ban a champion from the game. Ex: !b Teemo",
        "!ub <champ>: Unban a champion from the game. Ex: !ub Teemo",
        "!lb: List all banned champions.",
    ]
    command_list = "\n".join(commands)
    await ctx.send(f"Available commands:\n{command_list}")

# List all available champs for a selected gamemode
@bot.command(name="lc")
async def list_champs(ctx, gamemode = "melee"):
    champs = lobby.get_champs_for_gamemode(gamemode)
    if champs:
        champ_list = "\n".join(champs)
        await ctx.send(f"Champions available for {gamemode}:\n{champ_list}")
    else:
        await ctx.send("No champions available for this gamemode.")


bot.run(disc_token)

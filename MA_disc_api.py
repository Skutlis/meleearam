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


@bot.check
async def globally_check_channel(ctx):
    return ctx.channel.id == channel_id


# Example: Register a player with a gametag and store it in a database
@bot.command(name="reg")
async def register_player(ctx, gametag, tagline):
    discord_id = (
        ctx.author.id
    )  # Get the Discord ID of the person who executed the command
    discord_id = str(discord_id)

    # Call your existing logic to register the player in the database
    success = lobby.register_player(
        discord_id, gametag, tagline
    )  # Example function from your data_handler

    if success:
        await ctx.send(f"{ctx.author.name} has been registered as {gametag}#{tagline}.")
    else:
        await ctx.send(
            f"Could not find the universal Riot ID of {gametag}#{tagline}. Control that both the name and tagline are correct."
        )


# Example: Start a game and collect all members from the same voice channel
@bot.command(name="start")
async def start_game(ctx):
    # Get the voice channel of the command author
    voice_state = ctx.author.voice  # Check if the author is in a voice channel

    if voice_state is None or voice_state.channel is None:
        await ctx.send("You are not in a voice channel.")
        return

    voice_channel = voice_state.channel
    members = voice_channel.members  # Get all members in the voice channel

    if not members:
        await ctx.send("No other members in the voice channel.")
        return

    discord_ids = [str(member.id) for member in members]  # Collect all Discord IDs
    status, gameinfo = lobby.start(discord_ids)
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


@bot.command(name="r")
async def reset_lobby(ctx):
    lobby.reset()
    await ctx.send("Lobby has been reset.")


@bot.command(name="list")
async def list_lobby(ctx):
    players = lobby.get_players()
    if players:
        player_list = "\n".join(players)
        await ctx.send(f"Players in the lobby:\n{player_list}")
    else:
        await ctx.send("No players in the lobby.")


@bot.command(name="b")
async def ban_champ(ctx, champ):
    success = lobby.ban_champ(champ)
    if success:
        await ctx.send(f"{champ} has been banned.")
    else:
        await ctx.send(f"{champ} is already banned.")


@bot.command(name="ub")
async def unban_champ(ctx, champ):
    success = lobby.unban_champ(champ)
    if success:
        await ctx.send(f"{champ} has been unbanned.")
    else:
        await ctx.send(f"{champ} is not banned.")


@bot.command(name="lb")
async def list_banned_champs(ctx):
    banned_champs = lobby.list_banned_champs()
    if banned_champs:
        champ_list = "\n".join(banned_champs)
        await ctx.send(f"Banned champions:\n{champ_list}")
    else:
        await ctx.send("No champions are banned.")


@bot.command(name="lc")
async def available_commands(ctx):
    commands = [
        "!reg <gamertag> <tagline>: Register a player with a gamertag.",
        "!start: Start a game with all members in the voice channel.",
        "!r: Reset the lobby.",
        "!l: List all players in the lobby.",
        "!b <champ>: Ban a champion from the game.",
        "!ub <champ>: Unban a champion from the game.",
        "!lb: List all banned champions.",
    ]
    command_list = "\n".join(commands)
    await ctx.send(f"Available commands:\n{command_list}")


bot.run(disc_token)

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


bot.run(disc_token)

import discord # type: ignore
from discord.ext import commands # type: ignore
import logging # type: ignore
from dotenv import load_dotenv
import os # type: ignore

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    """
    Bot is ready!
    """

@bot.event
async def on_member_join(member):
    """
    When a member joins
    """

@bot.event
async def on_message(message):
    """
    When someone sends a message
    """

    # message.author is the one who sends the message
    # bot.user references the bot account
    if message.author == bot.user:
        return
    
    # message.content is the message content
    # await message.delete() deletes the message
    # message.channel accesses the channel
    # await channel.send() sends the message in the channel, where Member.mention pings the user

    await bot.process_commands(message) # processes the commands

@bot.command()
async def infect(ctx, infected: discord.Member):
    covid19 = discord.utils.get(ctx.author.roles, name="covid 19")
    if covid19:
        await infected.add_roles(covid19)
    
    brainrot = discord.utils.get(ctx.author.roles, name="brainrot")
    if brainrot:
        await infected.add_roles(brainrot)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
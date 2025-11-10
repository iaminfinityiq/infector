import discord # type: ignore
from discord.ext import commands, tasks # type: ignore
import logging # type: ignore
from dotenv import load_dotenv
import os # type: ignore
from sys import exit # type: ignore
import json # type: ignore
from time import time # type: ignore
from datetime import timedelta # type: ignore

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
general = int(os.getenv("GENERAL"))
server = int(os.getenv("SERVER_ID"))

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

@tasks.loop(seconds=1)
async def status_update():
    with open("data.json") as file:
        data = json.load(file)

    guild = bot.get_guild(server_id)
    for member in guild.members:
        covid19 = discord.utils.get(member.roles, name="covid 19")
        if covid19 and int(time()) - data[member.id]["infected_time"] > 259200:
            timeout_duration = timedelta(minutes=30)
            await user.timeout(timeout_duration, reason="Infected with covid 19 for more than 3 days")
            
            channel = bot.get_channel(general)
            await channel.send(f"User {member.mention} has been infected with covid 19 for more than 3 days. Because of that, {member.mention} will be timed out for 30 minutes!")

            data[str(member.id)]["infected_time"] = 0
            data[str(member.id)]["infect_time"] = 0
            member.remove_roles(covid19)

    with open("data.json") as file:
        data = json.load(file)

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
    with open("data.json") as file:
        data = json.load(file)

    if int(time()) - data[str(infected.id)]["infect_time"] < 86400:
        await ctx.send("You have already infect someone within 24 hours, please wait for a moment before you can infect someone")
        return
    
    if infected.id == 1435931107521593344:
        await ctx.send("Cannot infect the Infector himself")
        return

    admin = discord.utils.get(infected.roles, name="adm")
    if admin:
        await ctx.send(f"Cannot infect user {infected.mention} because {infected.mention} is an admin")
        return

    covid19 = discord.utils.get(ctx.author.roles, name="covid 19")
    if covid19:
        covid19 = discord.utils.get(infected.roles, name="covid 19")
        if covid19:
            await ctx.send(f"User {infected.mention} is already infected with covid 19")
        
        await infected.add_roles(covid19)
        await ctx.send(f"Successfully infect user {infected.mention} using covid 19")
            
        data[str(infected.id)]["infected_time"] = int(time.time())
        data[str(ctx.author.id)]["infect_time"] = int(time.time())
    else:
        await ctx.send(f"Cannot infect user {infected.mention} using covid 19 because you don't have that role")
    
    brainrot = discord.utils.get(ctx.author.roles, name="brainrot")
    if brainrot:
        await infected.add_roles(brainrot)
        await ctx.send(f"Successfully infect user {infected.mention} using brainrot")
        data[str(infected.id)]["infected_time"] = int(time.time())
        data[str(ctx.author.id)]["infect_time"] = int(time.time())
    else:
        await ctx.send(f"Cannot infect user {infected.mention} using brainrot because you don't have that role")

    with open("data.json", "w") as file:
        json.dump(data, file)

bot.run(token)




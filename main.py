import discord # type: ignore
from discord.ext import commands, tasks # type: ignore
import logging # type: ignore
from dotenv import load_dotenv
import os # type: ignore
from sys import exit # type: ignore
import json # type: ignore
from time import time # type: ignore
from datetime import timedelta # type: ignore
from random import randint # type: ignore

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
general = int(os.getenv("GENERAL"))
server = int(os.getenv("SERVER_ID"))
owner = int(os.getenv("OWNER_ID"))

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

@tasks.loop(seconds=60)
async def bot_loop():
    """
    Update loop for the bot, this runs every 60 seconds to avoid lagging
    """
    with open("data.json") as file:
        data = json.load(file)

    guild = bot.get_guild(server_id)
    covid_infected = False
    brainrot_infected = False
    channel = bot.get_channel(general)
    for member in guild.members:
        covid19 = discord.utils.get(member.roles, name="covid 19")
        if covid19 and int(time()) - data[member.id]["infected_time"] > 259200:
            covid_infected = True
            timeout_duration = timedelta(minutes=30)

            try:
                await user.timeout(timeout_duration, reason="Infected with covid 19 for more than 3 days")
            except Exception:
                await channel.send(f"User {member.mention} cannot be timed out")
            else:
                await channel.send(f"User {member.mention} has been infected with covid 19 for more than 3 days. Because of that, {member.mention} will be timed out for 30 minutes!")

            data[str(member.id)]["infected_time"] = 0
            data[str(member.id)]["infect_time"] = 0
            await member.remove_roles(covid19)

        brainrot = discord.utils.get(member.roles, name="brainrot")
        if brainrot:
            brainrot_infected = True

    covid19 = discord.utils.get(guild.roles, name="covid 19")
    brainrot = discord.utils.get(guild.roles, name="brainrot")
    if not covid_infected:
        idx = randint(0, len(guild.members)-1)
        origin = guild.members[idx]
        await origin.add_roles(covid19)
        await channel.send(f"Since there are no more person infected with covid 19, a new user getting infected with covid 19 is {origin.mention}")
        
        data[str(member.id)]["infected_time"] = int(time())

    if not brainrot_infected:
        idx = randint(0, len(guild.members)-1)
        origin = guild.members[idx]
        await origin.add_roles(brainrot)
        await channel.send(f"Since there are no more person infected with brainrot, a new user getting infected with brainrot is {origin.mention}")
    
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
    """
    Infects a user
    """
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

@bot.command()
async def print_data(ctx):
    if ctx.author.id == owner:
        with open("data.json", "r") as file:
            await ctx.send(str(json.load(file)))

bot.run(token)

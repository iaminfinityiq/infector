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
bot_id = int(os.getenv("BOT_ID"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    """
    Bot is ready!
    """
    with open("data.json", "r") as file:
        data = json.load(file)
    
    guild = bot.get_guild(server)
    covid19 = discord.utils.get(guild.roles, name="covid 19")
    brainrot = discord.utils.get(guild.roles, name="brainrot")
    for member in guild.members:
        data[str(member.id)]["infect_time"] = int(time())
        data[str(member.id)]["infected_time"] = int(time())
        if covid19:
            await member.remove_roles(covid19)

        if brainrot:
            await member.remove_roles(brainrot)

    with open("data.json", "w") as file:
        json.dump(data, file)
    
    if not bot_loop.is_running():
        bot_loop.start()

@bot.event
async def on_member_join(member):
    """
    When a member joins
    """
    with open("data.json", "r") as file:
        data = json.load(file)

    if str(member.id) not in data:
        data[str(member.id)]["infect_time"] = int(time())
        data[str(member.id)]["infected_time"] = int(time())

    with open("data.json", "w") as file:
        json.dump(data, file)

@tasks.loop(seconds=10)
async def bot_loop():
    """
    Update loop for the bot
    """
    with open("data.json", "r") as file:
        data = json.load(file)

    guild = bot.get_guild(server)
    covid_infected = False
    brainrot_infected = False
    channel = bot.get_channel(general)
    for member in guild.members:
        covid19 = discord.utils.get(member.roles, name="covid 19")
        if covid19:
            covid_infected = True
            if int(time()) - data[str(member.id)]["infected_time"] > 259200:
                timeout_duration = timedelta(minutes=30)
                try:
                    await member.timeout(timeout_duration, reason="Infected with covid 19 for more than 3 days")
                except Exception:
                    await channel.send(f"User {member.mention} cannot be timed out")
                else:
                    await channel.send(f"User {member.mention} has been infected with covid 19 for more than 3 days. Because of that, {member.mention} will be timed out for 30 minutes.")

                await member.remove_roles(covid19)
                data[str(member.id)]["infected_time"] = int(time())
                data[str(member.id)]["infect_time"] = int(time())

        brainrot = discord.utils.get(member.roles, name="brainrot")
        if brainrot:
            brainrot_infected = True

    covid19 = discord.utils.get(guild.roles, name="covid 19")
    brainrot = discord.utils.get(guild.roles, name="brainrot")
    if not covid_infected:
        members = [m for m in guild.members if not m.bot]
        origin = members[randint(0, len(members)-1)]
        await origin.add_roles(covid19)
        await channel.send(f"Since there are no more person infected with covid 19, a new user getting infected with covid 19 is {origin.mention}")
        
        data[str(origin.id)]["infected_time"] = int(time())

    if not brainrot_infected:
        members = [m for m in guild.members if not m.bot]
        origin = members[randint(0, len(members)-1)]
        await origin.add_roles(brainrot)
        await channel.send(f"Since there are no more person infected with brainrot, a new user getting infected with brainrot is {origin.mention}")
    
    with open("data.json", "w") as file:
        json.dump(data, file)

@bot_loop.error
async def bot_loop_error(error):
    channel = bot.get_channel(general)
    await channel.send(f"❌ Bot loop error: {error}")

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

    if int(time()) - data[str(ctx.author.id)]["infect_time"] < 86400:
        await ctx.send("You have already infect someone within 24 hours, or you are infected within your first hour, please wait for a moment before you can infect someone")
        return
    
    if infected.id == bot_id:
        await ctx.send("Cannot infect the Infector himself")
        return

    covid19 = discord.utils.get(ctx.author.roles, name="covid 19")
    if covid19:
        covid19_infected = discord.utils.get(infected.roles, name="covid 19")
        if covid19_infected:
            await ctx.send(f"User {infected.mention} is already infected with covid 19")
        else:
            await infected.add_roles(covid19)
            await ctx.send(f"Successfully infect user {infected.mention} using covid 19")
            
            data[str(infected.id)]["infected_time"] = int(time())
            data[str(ctx.author.id)]["infect_time"] = int(time())
            data[str(infected.id)]["infect_time"] = int(time()) - 82800 # Added a 1-hour cooldown after being infected to avoid mass infection
    else:
        await ctx.send(f"Cannot infect user {infected.mention} using covid 19 because you don't have that role")
    
    brainrot = discord.utils.get(ctx.author.roles, name="brainrot")
    if brainrot:
        brainrot_infected = discord.utils.get(infected.roles, name="brainrot")
        if brainrot_infected:
            await ctx.send(f"User {infected.mention} is already infected with brainrot")
        else:
            await infected.add_roles(brainrot)
            await ctx.send(f"Successfully infect user {infected.mention} using brainrot")
            data[str(ctx.author.id)]["infect_time"] = int(time())
            data[str(infected.id)]["infect_time"] = int(time()) - 43200
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












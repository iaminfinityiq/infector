import discord # type: ignore
from discord.ext import commands # type: ignore
import logging # type: ignore
from dotenv import load_dotenv
import os # type: ignore
import mysql.connector # type: ignore
from sys import exit

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
DB_HOST = os.environ.get("MYSQLHOST")
DB_PORT = os.environ.get("MYSQLPORT")
DB_USER = os.environ.get("MYSQLUSER")
DB_PASSWORD = os.environ.get("MYSQLPASSWORD")
DB_NAME = os.environ.get("MYSQLDATABASE")

def open_connection():
    global conn
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        exit(1)

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
    if infected.id == 1435931107521593344:
        await ctx.send("Cannot infect the Infector himself")
        return

    admin = discord.utils.get(infected.roles, name="adm")
    if admin:
        await ctx.send(f"Cannot infect user {infected.mention} because {infected.mention} is an admin")
        return

    covid19 = discord.utils.get(ctx.author.roles, name="covid 19")
    if covid19:
        await infected.add_roles(covid19)
        await ctx.send(f"Successfully infect user {infected.mention} using covid 19")
    else:
        await ctx.send(f"Cannot infect user {infected.mention} using covid 19 because you don't have that role")
    
    brainrot = discord.utils.get(ctx.author.roles, name="brainrot")
    if brainrot:
        await infected.add_roles(brainrot)
        await ctx.send(f"Successfully infect user {infected.mention} using brainrot")
    else:
        await ctx.send(f"Cannot infect user {infected.mention} using brainrot because you don't have that role")

@bot.command()
async def add_rows(ctx):
    """
    Adds all guild members to the DaysUntilCovid19 table with 0 days left.
    Skips members who are already in the table.
    """
    global conn
    open_connection()
    
    cursor = conn.cursor()

    cursor.execute("USE railway")
    sql = """
    INSERT INTO DaysUntilCovid19 (UserID, DaysLeft)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE DaysLeft = DaysLeft
    """  # This avoids duplicates

    try:
        for member in ctx.guild.members:
            if member.id != 1435931107521593344:
                cursor.execute(sql, (member.id, 0))

        conn.commit()
        await ctx.send("Added all members to the database (duplicates skipped).")
    except mysql.connector.Error as err:
        await ctx.send(f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

bot.run(token)

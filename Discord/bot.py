import datetime
from discord.ext import commands, tasks
import discord
from dataclasses import dataclass
import configparser
import os

""" Change the current directory so config loads right """
if os.path.dirname(__file__) != '':
    current_folder = os.path.dirname(__file__)
    os.chdir(current_folder)

config = configparser.ConfigParser()
config.read('./config.ini')

BOT_TOKEN = str(config['BOT_SETUP']['TOKEN'])
CHANNEL_ID = int(config['BOT_SETUP']['CHANNEL_ID'])
MAX_SESSION_TIME_MINUTES = config.getint('BOT_SETUP', 'MAX_SESSION_TIME')

@dataclass
class Session:
    is_active: bool = False
    start_time: int = 0

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
session = Session()

@bot.event
async def on_ready():
    print("Hello! Study bot is ready!")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Hello! Study bot is ready!")


@tasks.loop(minutes=MAX_SESSION_TIME_MINUTES, count=2)
async def break_reminder():

    # Ignore the first execution of this command.
    if break_reminder.current_loop == 0:
        return

    channel = bot.get_channel(CHANNEL_ID)
    await channel.send(f"**Take a break!** You've been studying for {MAX_SESSION_TIME_MINUTES} minutes.")

@bot.command()
async def start(ctx):
    if session.is_active:
        await ctx.send("A session is already active!")
        return

    session.is_active = True
    session.start_time = ctx.message.created_at.timestamp()
    human_readable_time = ctx.message.created_at.strftime("%H:%M:%S")
    break_reminder.start()
    await ctx.send(f"New session started at {human_readable_time}")


@bot.command()
async def end(ctx):
    if not session.is_active:
        await ctx.send("No session is active!")
        return

    session.is_active = False
    end_time = ctx.message.created_at.timestamp()
    duration = end_time - session.start_time
    human_readable_duration = str(datetime.timedelta(seconds=duration))
    break_reminder.stop()
    await ctx.send(f"Session ended after {human_readable_duration}.")


bot.run(BOT_TOKEN)
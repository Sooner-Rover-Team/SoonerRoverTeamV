import datetime
from discord.ext import commands, tasks
import discord
from dataclasses import dataclass
import configparser
import os
import prompts # file that contains all bot prompts/actions

"""
TODO: bot commands: roll dice, announce meetings, post links to stuff

MESSAGE is a structure containing the author, msg from author and channel the msg came from
@bot.event is a decorator that the bot uses to tell which function to call. It knows on_ready(), on_messsage(), on_member_join(), on_error(),
@bot.command is basically custom events. use @bot.command(name='x') where x is the command the user types in discord to call that function like --help
"""

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

# attempts to send a message to discord based on the users msg
async def send_message(message, user_message, is_private):
    try:
        response = prompts.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

def run_discord_bot():
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all()) # initialize bot, prefix is used with bot command events
    session = Session()

    @bot.event # function decorator, telling the bot to call this function when an event occurs
    async def on_ready(): 
        print("Hello! Study bot is ready!")
        channel = bot.get_channel(CHANNEL_ID)
        #await channel.send("Hello! Study bot is ready!")

    @bot.event
    async def on_member_join(member):
        await member.create_dm()
        await member.dm_channel.send(f'Hi {member.name}, welcome to the SORO Discord server! Type !help to get a list of my functions :)')

    @bot.event
    async def on_message(message): # bot knows to call this function when a msg is given because of the parameters
        if message.author == bot.user: # prevents the bot from responding to itself and creating an infinite loop
            return
        
        user_message = str(message.content)
        if user_message[0] != '!': return # each Remi command must start with !

        username = str(message.author)
        channel = str(message.channel)

        print(f"{username} said: '{user_message}' in ({channel})") # debug output

        if(user_message[1] == '!'): # !!msg to reply in your DM
            user_message = user_message[2:] # remove flag to process msg
            await send_message(message, user_message, is_private=True)
        else:
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=False)

    bot.run(BOT_TOKEN)

    # @bot.command(name='69') # if using on_message(), commands will be ignored since they are passed to on_message instead
    # async def meme(ctx):
    #     channel = bot.get_channel(CHANNEL_ID)
    #     await channel.send("LOLLLLL")


# @tasks.loop(minutes=MAX_SESSION_TIME_MINUTES, count=2)
# async def break_reminder():

#     # Ignore the first execution of this command.
#     if break_reminder.current_loop == 0:
#         return

#     channel = bot.get_channel(CHANNEL_ID)
#     await channel.send(f"**Take a break!** You've been studying for {MAX_SESSION_TIME_MINUTES} minutes.")

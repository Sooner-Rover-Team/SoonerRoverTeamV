import configparser
from dateutil.parser import parse as dtparse
import os
import datetime
import pytz
import discord
from discord.ext import commands, tasks
from dataclasses import dataclass
import prompts # file that contains all bot prompts/actions
from calendarUtil import *

# import discord.ext
#from dotenv import load_dotenv
#imports get_list_event() function from list_event.py

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

#initilaise load_dotenv() - loads .env file
#load_dotenv()
#Extracting api token from .env file
#TOKEN = os.getenv('DISCORD_TOKEN')

#bot = commands.Bot(command_prefix = '$')

TIME_FORMAT1='%H:%M'  #time format for the .strftime method
TIME_FORMAT2='%m/%d/%Y'


class Bot:
    def __init__(self) -> None:
        # initialize bot, prefix is used with bot command events
        self.bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    # attempts to send a message to discord based on the users msg
    async def send_message(self, message, user_message, is_private):
        try:
            response = prompts.handle_response(user_message)
            if not response: return
            await message.author.send(response) if is_private else await message.channel.send(response)
        except Exception as e:
            print(e)

    # creating a loop that runs every day at 9 AM UTC
    @tasks.loop(time=datetime.time(hour=4, minute=0))
    async def event_poster(self):
        print("time")
        number_events=10
        start=datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        end=datetime.datetime.utcnow().replace(hour=23, minute=59,
        second=59,microsecond=0).isoformat() + 'Z'
        event_dict_list = get_list_event(number_events,start,end)
        if len(event_dict_list) == 0:
            print("No events today")
            # embed=discord.Embed(title = "No Events Found", colour = 0xf74f18,
            # url="https://calendar.google.com/calendar/u/0/r?mode=week")
            # channel = self.bot.get_channel(CHANNEL_ID)
            # await channel.send(embed=embed)
        else:
            embed=discord.Embed(title = " :calendar_spiral: Upcoming Events Today",
            url="https://calendar.google.com/calendar/u/0/r?mode=week",
            description= f'There are {len(event_dict_list)} events today', colour = 0xf74f18)
            embed.set_thumbnail(url=
            "https://img.icons8.com/fluent/48/000000/google-calendar--v2.png")
            for event in event_dict_list:
                #set variables
                startdatetime = event["start_datetime"]
                enddatetime = event["end_datetime"]
                eventdescription = event["event_desc"]
                stime = datetime.datetime.strftime(dtparse(startdatetime),
                format=TIME_FORMAT1)
                etime = datetime.datetime.strftime(dtparse(enddatetime),
                format=TIME_FORMAT1)
                html_link = event["html_link"]
                title_description = event["eventtitle"]
                #embedding fields
                embed.add_field(name=f'{title_description} from {stime} to {etime}',
                value = f"[{eventdescription}]({html_link})", inline = False)
                embed.set_footer(text=
                f"For {datetime.datetime.strftime(dtparse(startdatetime), format=TIME_FORMAT2)}")
        channel = self.bot.get_channel(CHANNEL_ID)
        await channel.send(embed=embed)

    @event_poster.before_loop
    async def before_event_poster(self):
        print("Waiting...")
        await self.bot.wait_until_ready()
        print("Task loop is ready!")

    # @event_poster.after_loop
    # async def after_event_poster():
    #     if event_poster.is_being_cancelled():
    #         print("Event poster task was cancelled.")


    def run_discord_bot(self):

        @self.bot.event # function decorator, telling the bot to call this function when an event occurs
        async def on_ready():
            self.event_poster.start() 
            print("Hello! Study bot is ready!")
            channel = self.bot.get_channel(CHANNEL_ID)
            #await channel.send("Hello! Study bot is ready!")

        @self.bot.event
        async def on_member_join(member):
            await member.create_dm()
            await member.dm_channel.send(f'Hi {member.name}, welcome to the SORO Discord server! Type !help to get a list of my functions :)')

        @self.bot.event
        async def on_message(message): # bot knows to call this function when a msg is given because of the parameters
            if message.author == self.bot.user: # prevents the bot from responding to itself and creating an infinite loop
                return
            
            user_message = str(message.content)
            if user_message[0] != '!': return # each Remi command must start with !

            username = str(message.author)
            channel = str(message.channel)

            print(f"{username} said: '{user_message}' in ({channel})") # debug output

            if(user_message[1] == '!'): # !!msg to reply in your DM
                user_message = user_message[2:] # remove flag to process msg
                await self.send_message(message, user_message, is_private=True)
            else:
                user_message = user_message[1:]
                await self.send_message(message, user_message, is_private=False)
            await self.bot.process_commands(message) # allows commands to be called

        ##########################################################################################

        @self.bot.command("eventToday")
        async def getGCalEventsToday(ctx):
            print("get got")

        #returns upcoming events today
        @self.bot.command(name = 'eventstoday')
        # displays upcoming events today
        async def eventstoday(ctx,number_events=5):
            start=datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
            end=datetime.datetime.utcnow().replace(hour=23, minute=59,
            second=59,microsecond=0).isoformat() + 'Z'
            event_dict_list = get_list_event(number_events,start,end)
            if len(event_dict_list) == 0:
                embed=discord.Embed(title = "No Events Found", colour = 0xf74f18,
                url="https://calendar.google.com/calendar/u/0/r?mode=week")
                await ctx.send(embed=embed)
            else:
                embed=discord.Embed(title = f" :calendar_spiral: {len(event_dict_list)} Upcoming Events Today",
                url="https://calendar.google.com/calendar/u/0/r?mode=week",
                description= f"Let us know if you can't make it!", colour = 0xf74f18)
                embed.set_thumbnail(url=
                "https://img.icons8.com/fluent/48/000000/google-calendar--v2.png")
                for event in event_dict_list:
                    #set variables
                    startdatetime = event["start_datetime"]
                    enddatetime = event["end_datetime"]
                    eventdescription = event["event_desc"]
                    stime = datetime.datetime.strftime(dtparse(startdatetime),
                    format=TIME_FORMAT1)
                    etime = datetime.datetime.strftime(dtparse(enddatetime),
                    format=TIME_FORMAT1)
                    html_link = event["html_link"]
                    title_description = event["eventtitle"]
                    #embedding fields
                    embed.add_field(name=f'{title_description} from {stime} to {etime}',
                    value = f"[{eventdescription}]({html_link})", inline = False)
                    embed.set_footer(text=
                    f"For {datetime.datetime.strftime(dtparse(startdatetime), format=TIME_FORMAT2)}")
            await ctx.send(embed=embed)

        #returns the next days upcoming events
        @self.bot.command(name = 'eventstomorrow')
        async def eventstommorow(ctx,number_events=5):
            start = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).replace(hour=0,
            minute=0, second=0,microsecond=0).isoformat() + 'Z' # 'Z' indicates UTC time
            end =  datetime.datetime.utcnow().replace(hour=23, minute=59, second=59,
            microsecond=0).isoformat() + 'Z'
            event_dict_list = get_list_event(number_events,start,end)
            if len(event_dict_list) == 0:
                embed=discord.Embed(title = "No Events Found", colour = 0xf74f18,url=
                "https://calendar.google.com/calendar/u/0/r?mode=week")
                await ctx.send(embed=embed)
            else:
                embed=discord.Embed(title = " :calendar_spiral:Upcoming Events Tommorrow",
                url="https://calendar.google.com/calendar/u/0/r?mode=week",
                description= f'for upto {len(event_dict_list)} events ', colour = 0xf74f18)
                embed.set_thumbnail(url=
                "https://img.icons8.com/fluent/48/000000/google-calendar--v2.png")
                for event in event_dict_list:
                    #set variables
                    startdatetime = event["start_datetime"]
                    enddatetime = event["end_datetime"]
                    eventdescription = event["event_desc"]
                    stime = datetime.datetime.strftime(dtparse(startdatetime), format=TIME_FORMAT1)
                    etime = datetime.datetime.strftime(dtparse(enddatetime), format=TIME_FORMAT1)
                    html_link = event["html_link"]
                    title_description = event["eventtitle"]
                    #embedding fields
                    embed.add_field(name=f'{title_description} from {stime} to {etime}',
                    value = f"[{eventdescription}]({html_link})", inline = False)
                    embed.set_footer(text =
                    f"For {datetime.datetime.strftime(dtparse(startdatetime), format=TIME_FORMAT2)}")
            await ctx.send(embed=embed)

        #returns the previous days past events
        @self.bot.command(name = 'eventsyesterday')
        async def eventsyesterday(ctx,number_events=5):
            start = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).replace(hour=0,
            minute=0, second=0,microsecond=0).isoformat() + 'Z' # 'Z' indicates UTC time
            end =  datetime.datetime.utcnow().replace(hour=23,
            minute=59, second=59,microsecond=0).isoformat() + 'Z'
            event_dict_list = get_list_event(number_events,start,end)
            if len(event_dict_list) == 0:
                embed=discord.Embed(title = "No Events Found", colour = 0xf74f18,
                url="https://calendar.google.com/calendar/u/0/r?mode=week")
                await ctx.send(embed=embed)
            else:
                embed=discord.Embed(title = " :calendar_spiral:Past Events Yesterday",
                url="https://calendar.google.com/calendar/u/0/r?mode=week",
                description= f'for upto {len(event_dict_list)} events ', colour = 0xf74f18)
                embed.set_thumbnail(url=
                "https://img.icons8.com/fluent/48/000000/google-calendar--v2.png")
                for event in event_dict_list:
                    #set variables
                    startdatetime = event["start_datetime"]
                    enddatetime = event["end_datetime"]
                    eventdescription = event["event_desc"]
                    stime = datetime.datetime.strftime(dtparse(startdatetime), format=TIME_FORMAT1)
                    etime = datetime.datetime.strftime(dtparse(enddatetime), format=TIME_FORMAT1)
                    html_link = event["html_link"]
                    title_description = event["eventtitle"]
                    #embedding fields
                    embed.add_field(name=f'{title_description} from {stime} to {etime}',
                    value = f"[{eventdescription}]({html_link})", inline = False)
                    embed.set_footer(text =
                    f"For {datetime.datetime.strftime(dtparse(startdatetime), format=TIME_FORMAT2)}")
            await ctx.send(embed=embed)


        self.bot.run(BOT_TOKEN)
    

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

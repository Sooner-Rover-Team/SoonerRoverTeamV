from discord.ext import commands
import random
import bot

"""
Adding to bot:
@bot.event flat above function, async def 'funcName'
    function name is the command user needs to use with ! as prefix EX: !funcName
"""

github = 'https://github.com/Sooner-Rover-Team/SoonerRoverTeamV'
googleDrive = 'https://drive.google.com/drive/u/0/folders/0B6oziDhC71QDbzNELW1INmVkNHc?resourcekey=0-PflQo5ozmvI3AKt8fErFkw'

# Add to this function to create more prompts/responses for the bot
def handle_response(message) -> str:
    p_message = message.lower()
    
    if p_message == 'hello':
        return 'Hey there!'
    
    if p_message == 'roll':
        return f'You rolled a {str(random.randInt(1,6))}'
    
    if p_message == 'help':
        return "idk lol"
    
    if p_message == 'github':
        return f"Here's the link to the SORO GitHub Repository: {github}"
    
    if p_message == 'drive':
        return f"Here's the link to the SORO Google Drive: {googleDrive}"

    return "Sorry, that's not a command I know. type !help to see my commands"

# @bot.command()
# async def github(ctx):
#     print("Link to github is: {github}")
#     await ctx.send("Here is the link to the SORO GitHub Repository: {github}")

# @bot.command()
# async def github(ctx):
#     print("Link to google drive is: {googleDrive}")
#     await ctx.send("Here is the link to the SORO Google Drive: {googleDrive}")

# @bot.command()
# async def dice(ctx, fromInt, toInt):
#     if fromInt == None:
#         fromInt = 1
#     if toInt == None:
#         fromInt = toInt
#     await ctx.send("You rolled a {}")

# @bot.command()
# async def start(ctx):
#     if session.is_active:
#         await ctx.send("A session is already active!")
#         return

#     session.is_active = True
#     session.start_time = ctx.message.created_at.timestamp()
#     human_readable_time = ctx.message.created_at.strftime("%H:%M:%S")
#     break_reminder.start()
#     await ctx.send(f"New session started at {human_readable_time}")


# @bot.command()
# async def end(ctx):
#     if not session.is_active:
#         await ctx.send("No session is active!")
#         return

#     session.is_active = False
#     end_time = ctx.message.created_at.timestamp()
#     duration = end_time - session.start_time
#     human_readable_duration = str(datetime.timedelta(seconds=duration))
#     break_reminder.stop()
#     await ctx.send(f"Session ended after {human_readable_duration}.")



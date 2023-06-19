from discord.ext import commands
import random
import requests
import configparser
"""
Adding to bot:
@bot.event flat above function, async def 'funcName'
    function name is the command user needs to use with ! as prefix EX: !funcName
"""

config = configparser.ConfigParser()
config.read('./config.ini')

GIF_KEY = "YOUR_GIPHY_API_KEY"
NASA_KEY = str(config['API_KEY']['NASA_KEY'])

github = 'https://github.com/Sooner-Rover-Team/SoonerRoverTeamV'
googleDrive = 'https://drive.google.com/drive/u/0/folders/0B6oziDhC71QDbzNELW1INmVkNHc?resourcekey=0-PflQo5ozmvI3AKt8fErFkw'

# Add to this function to create more prompts/responses for the bot
def handle_response(message) -> str:
    p_message = message.lower()

    if p_message == 'help':
        response = """Type !! instead ! in these commands for me to respond in your DM (you can also call these commands there):
        **!hello** - hey there!
        **!roll** - rolls a 6 sided dice. Use '!roll x' to roll an x sided die
        **!github** - posts the link to the SORO Github repo
        **!drive** - posts the link to the SORO Google Drive
        **!quote** - be inspired by a random quote
        **!nasa** - get NASA Astronomy's pic of the day!
        **!mars** - get a random photo from curiosty's latest mission on mars!
        """
        return response
    
    if p_message == 'hello':
        return 'Hey there!'
    
    if p_message[:4] == 'roll':
        if len(p_message) > 4:
            try:
                return f'You rolled a {str(random.randint(1,int(p_message[5:])))}'
            except:
                return f'Sorry, that format was incorrect, type !roll x where x is an integer'
        return f'You rolled a {str(random.randint(1,6))}'
    
    if p_message == 'github':
        return f"Here's the link to the SORO GitHub Repository: {github}"
    
    if p_message == 'drive':
        return f"Here's the link to the SORO Google Drive: {googleDrive}"
    
    if p_message == 'quote':
        query = "https://api.quotable.io/random" 
        response = requests.get(query)
        return response.json()["content"]
    
    if p_message[:3] == 'gif':
        search_term = p_message[4:]
        url = f"https://api.giphy.com/v1/gifs/random?api_key={API_KEY}&tag={search_term}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            gif_url = data["data"]["images"]["original"]["url"]
            return gif_url
        else:
            return "Sorry, no GIFs were found"
        
    if p_message == 'nasa':
        url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            title = data["title"]
            image_url = data["url"]
            explanation = data["explanation"]
            return f"Title: {title} \n Explanation: {explanation} \n Image URL: {image_url}"
        else:
            return "Unable to fetch the NASA Astronomy Picture of the day :("
        
    if p_message == 'mars':
        rover_name = 'curiosity'
        sol = random.randint(1, 3000)
        url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover_name}/latest_photos?api_key={NASA_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["latest_photos"]:
                photos = data["latest_photos"]
                random_photo = random.choice(photos)
                return random_photo["img_src"]
        return None

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



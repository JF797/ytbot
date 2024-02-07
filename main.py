# imports
import discord
import re
import time
from datetime import datetime
from functions import *

# Datetime settings for file structures and logging
now = datetime.now()
timestampNow = now.strftime("%Y%m%d_%H%M%S")

# Directory configurations for local device. These will change depending on device running app
directory = "/tmp/outputs"
logLocation = directory + '/logs'
logFilePath = (logLocation+now.strftime("/%Y%m%d.log"))
cookiesLocation = (directory+"/cookies.txt")

try:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M:%S',
        filename=logFilePath,
        filemode='a',
    )
    print(logFilePath)
    logging.info('logging configured')
except (FileNotFoundError):
    logging.error(f'Log file not found in {logFilePath}. Re-run script again which should fix otherwise investigate.')

# Check directories exist. If they don't then they will be created.
checkDirExistsIfNoThenCreate(directory)
checkDirExistsIfNoThenCreate(logLocation)
checkFileExistsIfNoThenCreate(logFilePath)


# Configurations required for Discord
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Set token value from token.txt file in same directory as project.
with open("token", "r") as tokenFile:
    TOKEN = tokenFile.read()

# Constants / variables used in code
linkFound = False



# Main code
@client.event
async def on_ready():
    logging.info(f"logged in as {client.user.name}")
    logging.info(f"with user ID: {client.user.id}")

@client.event
async def on_message(message):
    logging.info(f'message {message}')
    username = str(message.author)
    userMessage = str(message.content)
    channelMessage = str(message.channel.name)
    logging.info(f'User:{username}: Content:{userMessage} | In:{channelMessage}')

    if message.author == client.user:
        return

    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    youtube_match = re.match(youtube_regex, userMessage)

    if youtube_match:
        # Output the YouTube link to the chat
        youtubeVideoName = getLinkName(userMessage)
        await message.delete()
        await message.channel.send(f'Found YouTube link for video titled: {youtubeVideoName}')
        time.sleep(0.5)
        await message.channel.send(f'Now downloading video')
        outputFile = compileFullOutputFilePath(timestampNow, youtubeVideoName, directory)
        downloadVideo(userMessage, outputFile)
        await message.channel.send(f'Video "{youtubeVideoName}" downloaded')
        # Have to change file name temporarily to allow discord to send the video
        changeVideoFileName(outputFile, (directory+"/temp.mp4"))
        try:
            await message.channel.send(file=discord.File(directory+"/temp.mp4"))

        except (FileNotFoundError):
            logging.error('Error uploading file: File could not be found')
            await message.channel.send(f'Could not upload video {youtubeVideoName} due to FileNotFound error.')
        # Change video name back to what it was to keep records.
        changeVideoFileName((directory+"/temp.mp4"), (compileFullOutputFilePath(timestampNow, youtubeVideoName, directory)))

    # commands
    if userMessage.lower() == '!help':
        await message.channel.send(f"This is a help message for {username}")
        return


client.run(TOKEN)

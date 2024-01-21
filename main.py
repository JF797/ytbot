# imports
import discord
from datetime import datetime
import logging
import re
import os
import time

# Configurations required for Discord
intents = discord.Intents.all()
client = discord.Client(intents=intents)
# Set token value from token.txt file in same directory as project.
with open("token", "r") as tokenFile:
    TOKEN = tokenFile.read()


# Datetime settings for file structures and logging
now = datetime.now()
timestampNow = now.strftime("%Y%m%d_%H%M%S")

# Directory configurations for local device. These will change depening on device running app
directory = "/tmp/outputs"
logLocation = directory + '/logs'
logFilePath = (logLocation+now.strftime("/%Y%m%d.log"))
cookiesLocation = (directory+"/cookies.txt")


# Constants / variables used in code
linkFound = False

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M:%S',
    filename=logFilePath,
    filemode='a'
)

def checkingCookiesExists(directory):
    if not os.path.exists(directory):
        logging.warning(f'Could not find cookies.txt file at {directory}. Please ensure this is added')
        return
    else:
        logging.info(f'Cookies.txt file found at {directory}')
        return
def checkDirExistsIfNoThenCreate(directory):
    if not os.path.exists(directory):
        logging.warning(f'Could not find directory {directory}, creating now.')
        os.mkdir(directory)
        logging.info(f'Directory: {directory} created.')
    else:
        logging.info(f'Directory {directory} already exists. Continuing')
        return

def checkFileExistsIfNoThenCreate(fileLocation):
    if not os.path.exists(fileLocation):
        logging.warning(f'Could not find file: {directory}, creating now.')
        os.system(f'touch {fileLocation}')
        logging.info(f'File: {fileLocation} created.')
    else:
        logging.info(f'File: {fileLocation} already exists. Continuing')
        return


def getLinkName(videoLink):
    return os.popen(f'yt-dlp --skip-download -e {videoLink}').read()


def compileFullOutputFilePath(fileTimestamp, fileTitle, directory):
    return f'{directory}/"{fileTimestamp}_{fileTitle}".mp4'

def downloadVideo(videoLink, videoFullPath):
    os.system(f'yt-dlp --output {videoFullPath} {videoLink}')
    return


# Main code

# Check main directory for downloads exists, if not then create it.
checkDirExistsIfNoThenCreate(directory)

# Check directory for logs exists, if not then create it.
# Check if today's log file exists, if not then create it.
checkDirExistsIfNoThenCreate(logLocation)
checkFileExistsIfNoThenCreate(logFilePath)

@client.event
async def on_ready():
    logging.info(f"logged in as {client.user.name}")
    logging.info(f"with user ID: {client.user.id}")


# logging
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
        await message.channel.send(file=discord.File(outputFile))
        # try:
        #     await message.channel.send(file=discord.File(outputFile))
        # except:
        #     print("nope")
        # await message.channel.send(f'YouTube link detected: {youtube_match.group(0)}')


    # commands
    if userMessage.lower() == '!help':
        await message.channel.send(f"This is a help message for {username}")
        return


client.run(TOKEN)

# imports
import discord
import re
import time
from datetime import datetime
from functions import *


# Datetime settings for file structures and logging
timestampNow = generateTimestamp()
now = datetime.now()
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

# Check that yt-dlp is installed and is executable using standard PATH value
checkApplicationInstalled("yt-dlp")


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

    tiktok_regex = (
        '^.*https:\/\/(?:m|www|vm)?\.?tiktok\.com\/((?:.*\b(?:(?:usr|v|embed|user|video)\/|\?shareId=|\&item_id=)(\d+))|\w+)')
    tiktok_match = re.match(tiktok_regex, userMessage)

    if tiktok_match:
        timestampNow = generateTimestamp()
        videoLink = extractLinkFromText(userMessage)
        print(f'link: {videoLink}')
        await message.channel.send(f'Found Tiktok link from {message.author.display_name} which is now being downloaded...\nVideo title: {getLinkName(videoLink)}')
        time.sleep(0.5)
        outputFile = compileFullOutputFilePath(timestampNow,'tiktok', directory)
        downloadVideo(videoLink, outputFile)
        changeVideoFileName(outputFile, (directory+"/temp.mp4"))
        try:
            await message.channel.send(file=discord.File(directory+"/temp.mp4"))
            await message.delete()
        except (FileNotFoundError):
            logging.error('Error uploading file: File could not be found')
        changeVideoFileName((directory+"/temp.mp4"), (compileFullOutputFilePath(timestampNow, 'tiktok', directory)))
        timestampNow = generateTimestamp()


    # commands
    if userMessage.lower() == '!help':
        await message.channel.send(f"This is a help message for {username}")
        return

    if '!manual' in userMessage.lower():
        timestampNow = generateTimestamp()
        videoLink = extractLinkFromText(userMessage)
        logging.info(f'Manual download initiated. Download link: {videoLink}')
        await message.channel.send(f'Found manual link from {message.author.display_name} which is now being downloaded...\nVideo title: {getLinkName(videoLink)}')
        outputFile = compileFullOutputFilePath(timestampNow, 'manual_download', directory)
        downloadVideo(videoLink, outputFile)
        time.sleep(10)
        changeVideoFileName(outputFile, (directory + "/temp.mp4"))
        print(f'after change: {outputFile}')
        try:
            await message.channel.send(file=discord.File(directory+"/temp.mp4"))
            await message.delete()

        except (FileNotFoundError):
            logging.error('Error uploading file: File could not be found')
            await message.channel.send(f'Could not upload video {outputFile} due to FileNotFound error.')
        except ('discord.errors.HTTPException: 413 Payload Too Large'):
            await message.channel.send('video was too large')
        # Change video name back to what it was to keep records.
        changeVideoFileName((directory+"/temp.mp4"), (compileFullOutputFilePath(timestampNow, outputFile, directory)))
        return


client.run(TOKEN)

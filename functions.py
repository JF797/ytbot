import os
import logging
import re
from datetime import datetime
from shutil import which

def checkApplicationInstalled(command):
    installationLocation = which(command)
    if installationLocation is not None:
        logging.info(f'Application is installed at location: {installationLocation}')
    else:
        logging.warning(f'Application not installed, please install before running this script. Should be at {installationLocation}')
        exit()

def checkingCookiesExists(directory):
    if not os.path.exists(directory):
        logging.warning(f'Could not find cookies.txt file at {directory}. Please ensure this is added')
        return
    else:
        logging.info(f'Cookies.txt file found at {directory}')
        return

def checkFileExistsIfNoThenCreate(fileLocation):
    if not os.path.exists(fileLocation):
        logging.warning(f'Could not find file: {fileLocation}, creating now.')
        os.system(f'touch {fileLocation}')
        logging.info(f'File: {fileLocation} created.')
    else:
        logging.info(f'File: {fileLocation} already exists. Continuing')
        return

def checkDirExistsIfNoThenCreate(directory):
    if not os.path.exists(directory):
        logging.warning(f'Could not find directory {directory}, creating now.')
        os.makedirs(directory, exist_ok=True)
        logging.info(f'Directory: {directory} created.')
    else:
        logging.info(f'Directory {directory} already exists. Continuing')
        return

def changeVideoFileName(fileLocation, newName):
    logging.info(f'File name being changed from {fileLocation} to {newName}')
    os.system(f'mv {fileLocation} {newName}')
    logging.info(f'File name change complete, new location is {newName}')
    return

def getLinkName(videoLink):
    return os.popen(f'yt-dlp --skip-download -e {videoLink}').read()

def compileFullOutputFilePath(fileTimestamp, fileTitle, directory):
    return f'{directory}/"{fileTimestamp}_{fileTitle}".mp4'

def downloadVideo(videoLink, videoFullPath):
    os.system(f'yt-dlp --output {videoFullPath} {videoLink}')
    return

def extractLinkFromText(text):
    linkRegex = (r'(https?://[^\s]+)')
    logging.info(f'Extracted link{re.findall(linkRegex, text)[0]} from text: {text}')
    return (re.findall(linkRegex, text)[0])

# Chcek that file size is over limit
def isFileTooBig(videoFile):
    fileSizeBytes=os.path.getsize(videoFile)
    if fileSizeBytes >= 10485760:
        return True, fileSizeBytes
    else:
        return False, fileSizeBytes

def generateTimestamp():
    now = datetime.now()
    logging.info(f'Taken timestamp for "now" at {now}')
    return now.strftime("%Y%m%d_%H%M%S")
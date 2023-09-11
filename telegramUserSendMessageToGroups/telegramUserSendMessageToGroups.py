import os
import sys
import time # for sleep
import codecs # for emoji support
import logging # for logging
import datetime # for logging
import traceback # for error handling
from telethon import TelegramClient, events, sync # for telegram use

## Author: Eusebiu Rizescu
## Email: rizescueusebiu@gmail.com

# pip3 install telethon

## Variables
api_id = "111111"
api_hash = '111111111111111111111111111'
groupsFile = "groups.txt" # Relative path to the groups file. One groupName per line.
sleepSecondsBetweenRuns = 30 # This should be lower that the smallest number of wait minutes for a group. 30 seconds is good.

## Needed variables
currentDir = os.getcwd()
lastUpdateEvent = 0

# Logging function
def getLogger():
  # Create logs folder if not exists
  if not os.path.isdir(os.path.join(currentDir, "logs")):
    try:
      os.mkdir(os.path.join(currentDir, "logs"))
    except OSError:
      print("Creation of the logs directory failed")
    else:
      print("Successfully created the logs directory")

  now = datetime.datetime.now()
  log_name = (f"{now.year}." + '{:02d}'.format(now.month) + "." +
              '{:02d}'.format(now.day) +
              "-telegramUserSendMessageToGroups.log")
  log_name = os.path.join(currentDir, "logs", log_name)
  logging.basicConfig(format='%(asctime)s  %(message)s', level=logging.NOTSET,
                      handlers=[
                      logging.FileHandler(log_name),
                      logging.StreamHandler()
                      ])
  return logging.getLogger()

# Function that sends a message to a groupName
def sendTelegramMessage(log, client, groupName, messageFile, imageFile):
  try:
    # Read message
    message = codecs.open(os.path.join(currentDir, messageFile), mode="r", encoding='utf-8').read()

    if imageFile == "":
      # Send only message
      client.send_message(groupName, message)
    else:
      # Send photo with caption
      client.send_file(groupName, imageFile, caption=message)

    return True
  except Exception as e:
    log.info(f"Error when sending Telegram message: {e}")
    tracebackError = traceback.format_exc()
    log.info(tracebackError)
    return False

# Function that read groups to send messages to from the file
# Groups file has the following format:
# my_special_group, 4, path_to_message, optional_path_to_image    <- first is the groupName, interval, path to message, path to image
def readGroups(log, oldDict):
  groups = open(os.path.join(currentDir, groupsFile), "r")
  groups = groups.read().replace("\r\n", os.linesep).replace("\n", os.linesep).split(os.linesep)

  groupsDict = {}
  # Get group name from
  for group in groups:
    group = group.strip()
    if group in ["", os.linesep]:
      continue
    groupName = group.split(",")[0].strip()
    messageInterval = float(group.split(",")[1].strip())
    messageFile = group.split(",")[2].strip()
    imageFile = group.split(",")[3].strip() if len(group.split(",")) == 4 else ""
    # Add the group to the dict
    groupsDict[groupName] = {
        "messageInterval":
        messageInterval,
        "messageFile":
        messageFile,
        "imageFile":
        imageFile,
        "lastMessageTimestamp":
        oldDict[groupName]["lastMessageTimestamp"]
        if groupName in oldDict.keys() else 0,
    }
  return groupsDict

# Main function
def mainFunction():
  log = getLogger()
  log.info("###################################################### New MAIN run")

  try:
    # Break if config files not found
    if os.path.isfile(os.path.join(currentDir, groupsFile)) is False:
      log.info(f"Groups file {groupsFile} not found. Exiting.")

    # At the start we assume that we should send messages to all groups
    oldGroupsDict = {}

    # Instantiate Telegram client
    client = TelegramClient('session_name', api_id, api_hash)
    client.start()

    # Main while
    while True:
      log.info("##################### New run")

      # Read the groups
      groups = readGroups(log, oldGroupsDict)

      log.info(f"Groups: {str(groups)}")

      # Send the message
      for group in groups.keys():

        log.info(f"### Processing group: {group}")
        now = time.time()

        if now - groups[group]["lastMessageTimestamp"] < groups[group]["messageInterval"] * 60:
          log.info("Time interval not already passed. Wait " + str(groups[group]["messageInterval"] * 60 - (now - groups[group]["lastMessageTimestamp"])) + " seconds.")
        else:
          log.info("Time interval passed. Sending message")
          status = sendTelegramMessage(log, client, group, groups[group]["messageFile"], groups[group]["imageFile"])
          if status == True:
            log.info("Message successfully sent.")
            groups[group]["lastMessageTimestamp"] = now
          else:
            log.info("Error, message not sent.")

      oldGroupsDict = groups
      # Sleep between runs
      log.info(f"Sleeping {str(sleepSecondsBetweenRuns)} seconds.")
      time.sleep(sleepSecondsBetweenRuns)

  except KeyboardInterrupt:
    log.info("Quit")
    sys.exit(0)
  except Exception as e:
    log.info(f"Fatal Error: {e}")
    tracebackError = traceback.format_exc()
    log.info(tracebackError)
    sys.exit(98)


##### BODY #####
if __name__ == "__main__":

  if len(sys.argv) != 1:
    log.info("Wrong number of parameters. Use: python telegramUserSendMessageToGroups.py")
    sys.exit(99)
  else:
    mainFunction()

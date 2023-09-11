import os
import sys
import asyncio # for async
import logging # for logging
import datetime # for logging
import traceback # for error handling
from telethon import TelegramClient # for telegram use

## Author: Eusebiu Rizescu
## Email: rizescueusebiu@gmail.com

# pip3 install telethon

## Variables
api_id = "aaa"
api_hash = "aaa"

groupsMappingFile = "mapping.txt" # Relative path to the message file. It will be created by script, in order to have a mapping between GroupName and ChatId

## Needed variables
currentDir = os.getcwd()

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
              '{:02d}'.format(now.day) + "-updateGroupMappings.py")
  log_name = os.path.join(currentDir, "logs", log_name)
  logging.basicConfig(format='%(asctime)s  %(message)s', level=logging.INFO,
                      handlers=[
                      logging.FileHandler(log_name),
                      logging.StreamHandler()
                      ])
  return logging.getLogger()

# For each run, get the updates of the bot and update the group mapping file with the new
# chat_ids. When a bot is added to a group, an update is accessible, and we parse that, and
# add the chat id to the group mapping file
def updateGroupsMapping(log):
  loop = asyncio.get_event_loop()
  coroutine = updateGroupsMappingHandler(log)
  loop.run_until_complete(coroutine)

async def updateGroupsMappingHandler(log):
  try:
    log.info("##### Run updateGroupsMapping")
    with open(os.path.join(currentDir, groupsMappingFile), 'w') as file:
      for chat in await telegramClient.get_dialogs():
        file.write(
            f"Name: <<<{chat.name}>>>, ChatId: <<<{str(chat.id)}>>>{os.linesep}"
        )

  except Exception as e:
    log.info(f"Error when getting Updates for bot: {e}")
    tracebackError = traceback.format_exc()
    log.info(tracebackError)

# Main function
def mainFunction():
  log = getLogger()
  log.info("###################################################### New MAIN run")

  try:
    # Create mappings group if not present
    if os.path.isfile(os.path.join(currentDir, groupsMappingFile)) is False:
      with open(os.path.join(currentDir, groupsMappingFile), "a") as f:
        f.write("")
    # Start the Telegram client
    log.info("Start client")
    global telegramClient
    telegramClient = TelegramClient("bot2", api_id, api_hash)
    telegramClient.start()

    # Update the groups where the user is in.
    updateGroupsMapping(log)

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
    log.info("Wrong number of parameters. Use: python updateGroupMappings.py")
    sys.exit(99)
  else:
    mainFunction()

import os
import sys
import json # for JSON manipulation
import logging # for logging
import datetime # for logging and parsing dates
import traceback # for error handling


##### Functions #####

# Logging function
def getLogger():
  baseDir = os.getcwd()
  # Create logs folder if not exists
  if not os.path.isdir(os.path.join(baseDir, "logs")):
    try:
      os.mkdir(os.path.join(baseDir, "logs"))
    except OSError:
      print("Creation of the logs directory failed")
    else:
      print("Successfully created the logs directory")

  now = datetime.datetime.now()
  log_name = (f"{now.year}." + '{:02d}'.format(now.month) + "." +
              '{:02d}'.format(now.day) + "-transformJSON.log")
  log_name = os.path.join(baseDir, "logs", log_name)
  logging.basicConfig(format='%(asctime)s  %(message)s', level=logging.NOTSET,
                      handlers=[
                      logging.FileHandler(log_name),
                      logging.StreamHandler()
                      ])
  return logging.getLogger()

# Main function that does all the flow from 2 input excels, to 4 output excels
def mainFunction(type, source, destination):
  # Initialize the logger
  log = getLogger()
  log.info("############################################# New run of script")
  log.info(f"Source: {source}")
  log.info(f"Destination: {destination}")

  try:
    # Check if source file exists
    if os.path.isfile(source) is False:
      log.info(f"Source file ({source}) does not exists. Exiting")
      sys.exit(1)

    # Read JSON
    sourceFile = open(source)
    inputJSON = json.load(sourceFile)
    #log.info(str(inputJSON))

    # Initialize the output
    returnJSON = {
        "questionId": inputJSON["questionId"],
        "questionTemplate": inputJSON["questionTemplate"],
        "question": inputJSON["question_en"],
        "difficulty": inputJSON["difficulty"],
        "answers": [],
    }

    i = 0
    while True:
      key = f"answers/{str(i)}/id"
      if key in inputJSON:
        returnJSON["answers"].append({
            "id":
            inputJSON[key],
            "label":
            inputJSON[f"answers/{str(i)}/label"],
        })
      else:
        break
      i += 1

    # Processing "options"
    returnJSON["options"] = []
    i = 0
    while True:
      key = f"options/{str(i)}/"
      if f"{key}type" not in inputJSON:
        break
      optionObject = {"type": inputJSON[f"{key}type"]}
      propsObject = {"hint": inputJSON[f"{key}props/hint_en"]}
      listObject = []
      j = 0
      while True:
        key2 = f"{key}props/list/{str(j)}/label_en"
        if key2 in inputJSON:
          listObject.append({"label":inputJSON[key2]})
        else:
          break
        j += 1

      propsObject["list"] = listObject
      optionObject["props"] = propsObject
      returnJSON["options"].append(optionObject)
      i += 1


    # Print the new JSON
    #log.info("\n" + json.dumps(returnJSON, indent=4))

    # Write to file
    try:
      fileWrite = open(destination, "w")
      fileWrite.write(json.dumps(returnJSON, indent=4))
      log.info("QuestionID " + returnJSON["questionId"] + " successfully transformed and written to file")
    except:
      log.info(f"ERROR when writing to file: {destination}")
      log.info("Transformed JSON was: ")
      log.info("\n" + json.dumps(returnJSON, indent=4))
      sys.exit(2)

  except KeyboardInterrupt:
      log.info("Quit")
      sys.exit(0)
  except Exception as e:
    log.info(f"FATAL ERROR: {e}")
    tracebackError = traceback.format_exc()
    log.info(tracebackError)
    sys.exit(99)


##### BODY #####
if __name__ == "__main__":

  if len(sys.argv) != 3:
    log = getLogger()
    log.info("Wrong number of parameters. Use: python transformJSON.py <source> <destination>")
    sys.exit(100)
  else:
    source = sys.argv[1]
    destination = sys.argv[2]
    mainFunction(type, source, destination)

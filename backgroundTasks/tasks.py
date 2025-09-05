import os
import time

def logCreator():
    global logCounter
    
    with open(f"./logs/{str(int(time.time()))}.txt", "w") as file:
        file.write(f"{time.time()}")
        file.close()
        print("log added")

def logsDeleter():
    try:
        for fileName in os.listdir("./logs/"):
            filePath = os.path.join("./logs",fileName)
            os.remove(filePath)
        print("Files deleted successfully")
    except: 
        print("There might be a problem while removing files")
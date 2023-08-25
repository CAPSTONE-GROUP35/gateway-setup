import json
import os
import pickle
from models.log import Log

def displayAllLogRecords(filePath):
    logList = readFromBinaryFileToLogList(filePath)

    if(logList == []):
        print("No records to display")
    else:
        #Display list of log records saved
        for log in logList:
            logOutput = str(log.id) +  " " + log.date + " " + log.time + " " + log.toAddress + " " + log.fromAddress + " " + log.subject +  " " + log.message + " "  +  log.type + " " + log.action
            print(logOutput)

def writeToBinaryFileFromLogList(writeBinFilePath, writeLogList):
    # Check if writeLogList contains records
    if(writeLogList != []):
        if(os.path.exists(writeBinFilePath)):
            # Write list to existing bin file
            with open(writeBinFilePath, "wb") as f:
                pickle.dump(writeLogList, f)
        else:
            newDirectory = os.path.dirname(writeBinFilePath)
            doesDirectoryExist = os.path.exists(newDirectory)
            if not doesDirectoryExist:
                print("Directory does NOT exist")
                os.makedirs(newDirectory)
                print("Directory has been created")

            # Write list to new bin file
            with open(writeBinFilePath, "wb") as f:
                pickle.dump(writeLogList, f)

def readFromBinaryFileToLogList(readBinFilePath):
    global count
    readLogList = []

    # Try to open file if it exists
    if(os.path.exists(readBinFilePath)):
        print("File does exist")

        if(os.stat(readBinFilePath).st_size == 0):
            print("File is empty, cannot open file")
        else:
            print("Opening file to get records")
            # Open binary file using pickle
            with open(readBinFilePath, "rb") as f:
                readLogList = pickle.load(f)

    else:
        newDirectory = os.path.dirname(readBinFilePath)
        doesDirectoryExist = os.path.exists(newDirectory)
        if not doesDirectoryExist:
            print("Directory does NOT exist")
            os.makedirs(newDirectory)
            print("Directory has been created")

        print("File does NOT exist")
        print("Creating new empty bin file")

        file = open(readBinFilePath,"x")
        file.close()

        print("New empty bin file created")

    return readLogList

def getLogListCount(filePath):
    count = 0
    logList = readFromBinaryFileToLogList(filePath)
    
    if(logList != []):
        #Count records stored in bin file
        for log in logList:
            count += 1
    
    return count


def addLogRecord(filePath):
    #Get Current Log Records
    logList = readFromBinaryFileToLogList(filePath)

    userInput = str(input("Please press 'Y' to add an log record: "))

    while userInput.lower() == "y":
        if(userInput.lower() == "y"):
            count = getLogListCount(filePath)
            count += 1
            logId = count
            logDate = input("Please enter date(YYYY-MM-DD): ")
            logTime = input("Please enter time (24H): ")
            logTo = input("Please enter to address: ")
            logFrom = input("Please enter from address: ")
            logSubject = input("Please enter email subject: ")
            logMessage = input("Please enter enter log message: ")
            logType = input("Please enter enter log type: ")
            logAction = input("Please enter the action taken: ")
            newLog = Log(logId, logDate, logTime, logTo, logFrom, logSubject, logMessage, logType, logAction)
            logList.append(newLog)
            userInput = str(input("Please press 'Y' to add ANOTHER log record: "))
        else:
            break
    
        #Write new log records to bin file
        writeToBinaryFileFromLogList(filePath, logList)

def getLogListActionCount(filePath):
    logList = readFromBinaryFileToLogList(filePath)
    actionList = {"Task" : "Total emails","Allowed" : 0, "Blocked" : 0}

    if(logList != []):
        #Count records stored in bin file
        for log in logList:
            if (log.action == "Allowed"):
                # Append to allowed list
                actionList["Allowed"] += 1
            else:
                # Append to blocked list
                actionList["Blocked"] += 1
    
    #print(actionList)
    return actionList

def getLogListTypeCount(filePath):
    logList = readFromBinaryFileToLogList(filePath)
    typeList = {"Task" : "Threats found", "Safe": 0, "Virus" : 0, "Spam" : 0, "Phishing" : 0}

    if(logList != []):
        #Count records stored in bin file
        for log in logList:
            if (log.type.lower() == "safe"):
                # Append to safe list
                typeList["Safe"] += 1
            elif(log.type.lower() == "virus"):
                # Append to virus list
                typeList["Virus"] += 1
            elif(log.type.lower() == "spam"):
                # Append to spam list
                typeList["Spam"] += 1
            elif(log.type.lower() == "phishing"):
                # Append to phishing list
                typeList["Phishing"] += 1
    
    #print(typeList)
    return typeList

#readFromBinaryFileToLogList('data/logs.bin')
#displayAllLogRecords('/data/logs.bin')
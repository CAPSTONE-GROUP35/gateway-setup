import json
import os
import pickle
from models.log import Log


def displayAllLogRecords(filePath):
    logList = readFromBinaryFileToLogList(filePath)

    if (logList == []):
        print("No records to display")
    else:
        # Display list of log records saved
        for log in logList:
            print(log)


def writeToBinaryFileFromLogList(writeBinFilePath, writeLogList):
    if (os.path.exists(writeBinFilePath)):
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
    if (os.path.exists(readBinFilePath)):
        print("File does exist")

        if (os.stat(readBinFilePath).st_size == 0):
            print("File is empty, cannot open file")
        else:
            print("Opening file to get records")
            # Open binary file using pickle
            with open(readBinFilePath, "rb") as f:
                readLogList = pickle.load(f)

    return readLogList


def getLogListCount(filePath):
    count = 0
    logList = readFromBinaryFileToLogList(filePath)

    if (logList != []):
        # Count records stored in bin file
        for log in logList:
            count += 1

    return count


def addLogRecord(filePath):
    # Get Current Log Records
    logList = readFromBinaryFileToLogList(filePath)

    userInput = str(input("Please press 'Y' to add an log record: "))

    while userInput.lower() == "y":
        if (userInput.lower() == "y"):
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
            newLog = Log(logId, logDate, logTime, logTo, logFrom,
                         logSubject, logMessage, logType, logAction)
            logList.append(newLog)
            userInput = str(
                input("Please press 'Y' to add ANOTHER log record: "))
        else:
            break

        # Write new log records to bin file
        writeToBinaryFileFromLogList(filePath, logList)


def getLogListActionCount(filePath):
    logList = readFromBinaryFileToLogList(filePath)
    actionList = {"Task": "Total emails", "Allowed": 0, "Blocked": 0}

    if (logList != []):
        # Count records stored in bin file
        for log in logList:
            if (log.action.lower() == "allowed"):
                # Append to allowed list
                actionList["Allowed"] += 1
            else:
                # Append to blocked list
                actionList["Blocked"] += 1

    # print(actionList)
    return actionList


def getLogListTypeCount(filePath):
    logList = readFromBinaryFileToLogList(filePath)
    typeList = {"Task": "Threats found", "No threat": 0,
                "Virus or malware": 0, "Spam or phishing": 0}

    if (logList != []):
        # Count records stored in bin file
        for log in logList:
            if (log.type.lower() == "no_threat"):
                # Append to safe list
                typeList["No threat"] += 1
            elif (log.type.lower() == "virus_malware"):
                # Append to virus/malware list
                typeList["Virus or malware"] += 1
            elif (log.type.lower() == "spam_phishing"):
                # Append to spam/phishing list
                typeList["Spam or phishing"] += 1

    # print(typeList)
    return typeList


def clearLogList(filePath):
    logList = []
    writeToBinaryFileFromLogList(filePath, logList)

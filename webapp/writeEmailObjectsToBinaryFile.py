import os
import pickle
from models.email import Email


def displayAllEmailRecords(filePath):
    emailList = readFromBinaryFileToEmailList(filePath)

    if (emailList == []):
        print("No records to display")
    else:
        # Display list of email records saved
        for email in emailList:
            print(email)


def writeToBinaryFileFromEmailList(writeBinFilePath, writeEmailList):
    if (os.path.exists(writeBinFilePath)):
        # Write list to existing bin file
        with open(writeBinFilePath, "wb") as f:
            pickle.dump(writeEmailList, f)
    else:
        newDirectory = os.path.dirname(writeBinFilePath)
        doesDirectoryExist = os.path.exists(newDirectory)
        if not doesDirectoryExist:
            print("Directory does NOT exist")
            os.makedirs(newDirectory)
            print("Directory has been created")

        # Write list to new bin file
        with open(writeBinFilePath, "wb") as f:
            pickle.dump(writeEmailList, f)


def readFromBinaryFileToEmailList(readBinFilePath):
    global count
    readEmailList = []

    # Try to open file if it exists
    if (os.path.exists(readBinFilePath)):
        print("File does exist")

        if (os.stat(readBinFilePath).st_size == 0):
            print("File is empty, cannot open file")
        else:
            print("Opening file to get records")
            # Open binary file using pickle
            with open(readBinFilePath, "rb") as f:
                readEmailList = pickle.load(f)

    return readEmailList


def getEmailListCount(filePath):
    count = 0
    emailList = readFromBinaryFileToEmailList(filePath)

    if (emailList != []):
        # Count records stored in bin file
        for email in emailList:
            count += 1

    return count


def addEmailRecord(filePath):
    # Get Current Email Records
    emailList = readFromBinaryFileToEmailList(filePath)

    userInput = str(input("Please press 'Y' to add an email object: "))

    while userInput.lower() == "y":
        if (userInput.lower() == "y"):
            count = getEmailListCount(filePath)
            count += 1
            emailId = count
            emailToAddress = input("Please enter email to address: ")
            emailFromAddress = input("Please enter email from address: ")
            emailSubject = input("Please enter email subject: ")
            emailBody = input("Please enter email body: ")
            emailOriginal = input("Please input original email: ")

            newEmail = Email(emailId,
                             emailToAddress,
                             emailFromAddress,
                             emailSubject,
                             emailBody,
                             emailOriginal)
            emailList.append(newEmail)
            userInput = str(
                input("Please press 'Y' to add ANOTHER email object: "))
        else:
            break

        # Write new email records to bin file
        writeToBinaryFileFromEmailList(filePath, emailList)


def getOriginalEmail(id, filePath):
    originalEmail = ""

    # Get Current Email Records
    emailList = readFromBinaryFileToEmailList(filePath)

    if (emailList != []):
        for email in emailList:
            if (int(email.id) == int(id)):
                originalEmail = email.originalEmail

    return originalEmail


def clearEmailList(filePath):
    emailList = []
    writeToBinaryFileFromEmailList(filePath, emailList)

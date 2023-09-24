# This file is used to create Email
# and Log records by using a terminal menu system
import writeEmailObjectsToBinaryFile
import writeLogObjectsToBinaryFile


def displayAllEmailRecords():
    writeEmailObjectsToBinaryFile.displayAllEmailRecords('data/emails.bin')


def displayAllLogRecords():
    writeLogObjectsToBinaryFile.displayAllLogRecords('data/logs.bin')


def addEmailRecord():
    writeEmailObjectsToBinaryFile.addEmailRecord('data/emails.bin')


def addLogRecord():
    writeLogObjectsToBinaryFile.addLogRecord('data/logs.bin')


def clearEmailRecords():
    try:
        writeEmailObjectsToBinaryFile.clearEmailList('data/emails.bin')
        print("Email records successfully cleared")
    except:
        print("An error occured when trying to clear emails records")


def clearLogRecords():
    try:
        writeLogObjectsToBinaryFile.clearLogList('data/logs.bin')
        print("Log records successfully cleared")
    except:
        print("An error occurred when trying to clear log records.")


def validateInput(message):
    while True:
        try:
            userInput = int(input(message))
        except ValueError:
            print("Not a valid number, please try again.")
        else:
            return userInput
            break


print("\nWelcome to utility program for creating records," +
      "please choose one of the following options")
print("\nMain Menu")
print("1. Display all email records")
print("2. Display all log records")
print("3. Add email record")
print("4. Add log record")
print("5. Clear email records")
print("6. Clear log records")
print("7. Exit program")

menuOption = validateInput("Enter menu selection number: ")

while menuOption != 7:
    if (menuOption != 7):
        if (menuOption == 1):
            displayAllEmailRecords()
        elif (menuOption == 2):
            displayAllLogRecords()
        elif (menuOption == 3):
            addEmailRecord()
        elif (menuOption == 4):
            addLogRecord()
        elif (menuOption == 5):
            clearEmailRecords()
        elif (menuOption == 6):
            clearLogRecords()
        else:
            print("Invalid menu option, please try again")
    else:
        break
    print("\nMain Menu")
    print("1. Display all email records")
    print("2. Display all log records")
    print("3. Add email record")
    print("4. Add log record")
    print("5. Clear email records")
    print("6. Clear log records")
    print("7. Exit program")
    menuOption = validateInput("Enter menu selection number: ")

#!/usr/bin/env python
import email
import re
import sys
import os
import re
import utilities
from models.email import Email
from models.log import Log
from datetime import date
from datetime import time
from enum import Enum
from subprocess import run
from email import policy

# This script must return an exit code of 0 or 1
# Exit code 0: No threat detected. This exit code will result in the email being delivered to the intended recipient.
# Exit code 1: Threat detected. This exit code will result in the email being discarded.

class Outcome(Enum):
    ALLOWED = 0
    DENIED = 1

emailStr = sys.stdin.read()

# Email in object form with each element (To, From, Subject, etc.) mapped to an object property.
emailObj = email.message_from_string(emailStr, policy=email.policy.default)

# Check and print "To" address
emailToAddress = emailObj['To']

# Check and print "Subject"
emailSubject = emailObj['Subject']

# Check and extract "From" address using regex
fromDetails = emailObj['From']
emailRegex = r'<([^>]+)>'

match = re.search(emailRegex, fromDetails)

emailFromAddress = match.group(1)

emailBody = emailObj.get_body(('plain',)).get_content()

exitCode = Outcome.ALLOWED.value

regex = r'@(.*)'
if re.findall(regex, emailFromAddress)[0] == "internal.test":
    print("outbound email that needs to be encrypted")
else:
    print("inbound email that needs to be scanned")
    keywordBlacklist = ["casino", "lottery", "viagra"]
    emailOutcome = Outcome.ALLOWED.name
    logMessage = "The email body did not contain any suspicious words."

    # Keyword scanning
    for keyword in keywordBlacklist:
        if re.search(keyword, emailStr, re.IGNORECASE):
            emailOutcome = Outcome.DENIED.name
            exitCode = Outcome.DENIED.value
            logMessage = "The word %s was found in the email." % keyword
            break

    # Attachment scanning
    homeDir = "/home/user/"
    run(['ripmime', '-i', '-', '-d', 'attachments/'], cwd=homeDir, input=emailStr, text=True)  # Extract attachments
    scanResult = run(['clamscan', 'attachments/'], cwd=homeDir, capture_output=True, text=True).stdout  # Scan attachments
    run(['rm', '-r', 'attachments/'], cwd=homeDir)  # Delete extracted attachments
    infectedCount = re.findall(r'Infected files: (.+)', scanResult)[0]  # Get infected attachment count

    if infectedCount != "0":
        emailOutcome = Outcome.DENIED.name
        exitCode = Outcome.DENIED.value
        logMessage = "Infected attachment detected"

    # Create and Add Email record
    emailCount = utilities.readListCount('../../webapp/data/emails.bin')
    emailCount += 1
    emailId = emailCount

    # Create Email Object
    emailRecord = Email(emailId, emailToAddress, emailFromAddress, emailSubject, emailBody)

    # Get current email records and add Email record to list
    emailList = []
    emailList = utilities.readFromBinaryFileToEmailList('../../webapp/data/emails.bin')
    emailList.append(emailRecord)

    # Write the updated Email List to bin file
    utilities.writeToBinaryFileFromEmailList('../../webapp/data/emails.bin')
    #################################### Create email record   ########################################

    # TODO: Add To, From and subject from Email variable
    #################################### Create new Log Record ########################################
    # Create and Add Log record
    logCount = utilities.readListCount('../../webapp/data/logs.bin')
    logCount += 1
    logId = logCount
    logDate = date.today()
    logTime = time.strftime('%H:%M:%S')
    logTo = "user@group35.com"
    logFrom = "admin@group35.com"
    logSubject = "Please meet in boardroom at 1PM"

    # Create Log object
    logRecord = Log(logId, logDate, logTime, logTo, logFrom, logSubject, logMessage, emailOutcome)

    # Get current log records and add Log record to list
    logList = []
    logList = utilities.readFromBinaryFileToLogList('../../webapp/data/logs.bin')
    logList.append(logRecord)

    # Write the updated Log List to bin file
    utilities.writeToBinaryFileFromLogList('../../webapp/data/logs.bin', logList)
    #################################### Create new Log Record ########################################

    
    
    
print(logMessage)


sys.exit(exitCode)

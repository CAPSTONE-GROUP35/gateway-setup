#!/usr/bin/env python

import sys
import re
import utilities
from models.email import Email
from models.log import Log
from datetime import date
from datetime import time
from enum import Enum

# This script must return an exit code of 0 or 1
# Exit code 0: No threat detected. This exit code will result in the email being delivered to the intended recipient.
# Exit code 1: Threat detected. This exit code will result in the email being discarded.

class Outcome(Enum):
    ALLOWED = 0
    DENIED = 1

email = sys.stdin.read()
keywordBlacklist = ["casino", "lottery", "viagra"]
emailOutcome = Outcome.ALLOWED.name
exitCode = Outcome.ALLOWED.value
logMessage = "The email body did not contain any suspicious words."

for keyword in keywordBlacklist:
    if re.search(keyword, email, re.IGNORECASE):
        emailOutcome = Outcome.DENIED.name
        exitCode = Outcome.DENIED.value
        logMessage = "The word %s was found in the email." % keyword
        break

# TODO: Add email to, from, subject and body from Email variable
#################################### Create email record   ########################################
# Create and Add Email record
emailCount = utilities.readListCount('../../webapp/data/emails.bin')
emailCount += 1
emailId = emailCount
emailToAddress = "to@Email.com"
emailFromAddress = "from@Email.com"
emailSubject = "I am an email subject"
emailBody = "i am email body"

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
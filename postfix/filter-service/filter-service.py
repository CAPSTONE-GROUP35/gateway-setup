#!/usr/bin/env python
import email
import re
import sys
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

# Raw email in string format
emailStr = sys.stdin.read()

# Email in object form with each element (To, From, Subject, etc.) mapped to an object property.
emailObj = email.message_from_string(emailStr, policy=email.policy.default)

# Get 'from' address
fromDetails = emailObj['From']
emailFromregex = r'<([^>]+)>'
match = re.search(emailFromregex, fromDetails)
emailFromAddress = match.group(1)

# Get other elements
emailToAddress = emailObj['To']
emailSubject = emailObj['Subject']
emailBody = emailObj.get_body(('plain',)).get_content()

exitCode = Outcome.ALLOWED.value

domainRegex = r'@(.*)'
if re.findall(domainRegex, emailFromAddress)[0] == "internal.test":
    # Outbound emails logic
    # Keyword list scanning for outgoing emails
    logMessage = "The outgoing email did not contain any sensitive content."
    protectedKeywordList = ["secret", "confidential", "private"]
    for keyword in protectedKeywordList:
        if re.search(keyword, emailBody, re.IGNORECASE):
            # Give the email a new body, overwriting the old one
            newBody = "Encrypted message attached"
            emailObj.set_content(newBody)

            # Pipe oldBody into gpg and save symetrically encrypted 'encrypted.gpg' file
            filename = "encrypted.gpg"
            gpgPassphrase = "open"
            run(['gpg', '--output', filename, '--symmetric', '--passphrase', gpgPassphrase, '--batch', '--yes'], cwd='/home/user/', input=emailBody, text=True)

            # Get encrypted.gpg file
            with open(f'/home/user/{filename}', 'rb') as file:
                data = file.read()

            # Attach encrypted.gpg to email
            emailObj.add_attachment(data, maintype='application', subtype='octet-stream', filename=filename)

            # Overwrite the original email with the new version. New version will be piped back into postfix via filter-handler.sh for delivery
            with open('/home/user/temp-email-file.tmp', 'w') as file:
                file.write(emailObj.as_string())
            
            logMessage = "The word %s was found in the email. Encrypting outgoing email." % keyword
            break

else:
    #Inbound emails logic
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
    emailCount = utilities.getEmailListCount('../../webapp/data/emails.bin')
    emailCount += 1
    emailId = emailCount

    # Create Email Object
    emailRecord = Email(emailId, emailToAddress, emailFromAddress, emailSubject, emailBody, emailStr)

    # Get current email records
    emailList = utilities.readFromBinaryFileToEmailList('../../webapp/data/emails.bin')

    # Append Email record to the list
    emailList.append(emailRecord)

    # Write the updated Email List to bin file
    utilities.writeToBinaryFileFromEmailList('../../webapp/data/emails.bin', emailList)
    #################################### Create email record   ########################################

    # TODO: Add To, From and subject from Email variable
    #################################### Create new Log Record ########################################
    # Create and Add Log record
    logCount = utilities.getLogListCount('../../webapp/data/logs.bin')
    logCount += 1
    logId = logCount
    logDate = date.today()
    logTime = "11:32"
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

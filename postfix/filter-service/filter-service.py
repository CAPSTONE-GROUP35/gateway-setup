#!/usr/bin/env python
import email
import re
import sys
import os
import re
import random
import string
import utilities
import datetime
from models.email import Email
from models.log import Log
from enum import Enum
from subprocess import run
from email import policy

# This script must return an exit code of 0 or 1
# Exit code 0: No threat detected. This exit code will
# result in the email being delivered to the intended recipient.
# Exit code 1: Threat detected. This exit code will result in
# the email being discarded.

# Generate random string to facilitate synchronous filter service operations
randomChars = ''.join(random.choices(
    string.ascii_uppercase + string.digits, k=32))


class Outcome(Enum):
    ALLOWED = 0
    DENIED = 1


class ThreatType(Enum):
    SPAM_PHISHING = "spam_phishing"
    VIRUS_MALWARE = "virus_malware"
    NO_THREAT = "no_threat"

# Raw email in string format
emailStr = sys.stdin.read()

# Email in object form with each element (To, From, Subject, etc.)
# mapped to an object property.
emailObj = email.message_from_string(emailStr, policy=email.policy.default)

# Get 'from' address
fromDetails = emailObj['From']
emailFromregex = r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)'
match = re.search(emailFromregex, fromDetails)
emailFromAddress = match.group()

# Get other elements
emailToAddress = emailObj['To']
emailSubject = emailObj['Subject']
emailBody = emailObj.get_body(('plain',)).get_content()

exitCode = Outcome.ALLOWED.value

domainRegex = r'@(.*)'
if re.findall(domainRegex, emailFromAddress)[0] == "internal.test":
    # Outbound emails logic
    # Keyword list scanning for outgoing emails
    logMessage = "OUTBOUND: No email encryption required. "
    + "No sensitive words detected."
    protectedKeywordList = ["secret", "confidential", "private",
                            "sensitive", "protected", "classified",
                            "encryption", "encrypt", "decrypt",
                            "personal", "access control",
                            "access levels", "priv",
                            "privilege level", "privilege account",
                            "admin account", "password", "passcode",
                            "passphrase", "internal use only",
                            "internal only", "not for distribution",
                            "not for public", "not public",
                            "not for publication", "not for external",
                            "identity", "PII", "department specific",
                            "do not share", "do not copy",
                            "copying prohibited", "restricted",
                            "restrict access", "permission", "covert",
                            "concealed", "digital certificate",
                            "request for access", "change of privilege",
                            "change access", "change of access",
                            "data breach", "data protection",
                            "data security", "data loss",
                            "group policy", "secure storage",
                            "secure message", "administrative controls",
                            "IP address", "system security",
                            "breach", "information asset",
                            "unauthorized", "untrused", "phone number",
                            "residential address", "street address",
                            "signature", "passport", "mishandling",
                            "misconduct", "bank account", "savings account",
                            "credit card", "code", "token",
                            "identification number", "licence number",
                            "date of birth", "DOB", "mailing address",
                            "vulnerability", "caution", "money",
                            "financial", "finance", "cost", "threat",
                            "attack", "fraud", "anti-virus", "exploit",
                            "ransom", "malware", "virus", "trojan",
                            "worm"]

    for keyword in protectedKeywordList:
        if re.search(keyword, emailBody, re.IGNORECASE):
            logMessage = "OUTBOUND: Encrypting email. "
            + "Sensitive word '%s' detected." % keyword

            # Give the email a new body, overwriting the old one
            newBody = "Encrypted message attached"
            emailObj.set_content(newBody)

            # Pipe oldBody into gpg and save symetrically
            # encrypted file that will be attached to the email
            encryptedAttachmentPath = f'/home/user/encrypted-{randomChars}.gpg'
            gpgPassphrase = "open"
            run(['gpg', '--output', encryptedAttachmentPath, '--symmetric',
                '--passphrase', gpgPassphrase, '--batch', '--yes'],
                input=emailBody, text=True)

            # Get encrypted file
            with open(encryptedAttachmentPath, 'rb') as file:
                data = file.read()

            # Attach encrypted file to email
            emailObj.add_attachment(data, maintype='application',
                                    subtype='octet-stream',
                                    filename="encrypted.gpg")

            # Overwrite the original email with the new version.
            # New version will be piped back into postfix
            # via filter-handler.sh for delivery
            emailFilePath = sys.argv[1]
            with open(emailFilePath, 'w') as file:
                file.write(emailObj.as_string())

            # Delete encrypted file
            run(['rm', encryptedAttachmentPath])

            break

else:
    # Inbound emails logic
    keywordBlacklist = ["casino", "lottery", "viagra", "$$$",
                        "4U", "Accept credit cards", "act now",
                        "don't hesitate", "additional income",
                        "all natural", "apply online",
                        "auto email removal", "avoid bankruptcy",
                        "be amazed", "be your own boss",
                        "big bucks", "billing address",
                        "billion dollars", "brand new pager",
                        "bulk email", "buy direct", "cable converter",
                        "call free", "call now", "calling creditors",
                        "can't live without", "cancel at any time",
                        "any other offer", "cash bonus", "cashcashcash",
                        "check or money", "click below", "click here link",
                        "click to remove", "compare rates",
                        "complete for your business", "all orders",
                        "congratulations", "consolidate debt",
                        "credit card offer", "cure", "dear email",
                        "dear friend", "dear somebody", "dig up dirt",
                        "direct email", "direct marketing", "do it today",
                        "don't delete", "drastically reduced", "earn per week",
                        "easy terms", "eliminate", "bad credit",
                        "expect to earn", "fantastic deal",
                        "fast delivery", "finanical freedom",
                        "find out anything", "for free", "instant access",
                        "just $", "free access", "free consultation",
                        "free hosting", "free installation", "free investment",
                        "free membership", "free money", "free offer",
                        "free preview", "free priority", "free quote",
                        "free trial", "free website", "full refund",
                        "get it now", "get paid", "get started",
                        "gift certificate", "great offer", "guarantee",
                        "have you been turned down", "join millions",
                        "limited time only", "lose weight",
                        "lower interest rates", "lower monthly payment",
                        "lowest price", "luxury car", "meet singles",
                        "MLM", "money back", "money making", "trial offer",
                        "mortgage rates", "new customers only",
                        "new domain extensions", "nigerian",
                        "no age restrictions", "no catch", "no claim",
                        "no cost", "no credit", "no fees", "no gimmick",
                        "no investment", "medical exam", "no purchase",
                        "no selling", "no strings attached", "off shore",
                        "offer expires", "coupon", "extra cash",
                        "once in a lifetime", "100%",
                        "one hundred percent free", "biz",
                        "online pharmacy", "only $", "opt in",
                        "order now", "order status", "orders shipped",
                        "outstanding", "please read", "potential earnings",
                        "profits", "promise you", "pure profit", "real thing",
                        "refinance", "risk free", "safeguard notice",
                        "satisfaction", "save $", "save big money",
                        "save up to", "score with", "see for yourself",
                        "serious cash", "serious only", "shopping spree",
                        "sign up free", "social security", "security number",
                        "special promotion", "on sale",
                        "supplies are limitied", "take action", "best rates",
                        "your money", "isn't junk", "isn't spam",
                        "unlimited", "unsecured", "urgent",
                        "hate spam", "what are you waiting for",
                        "while supplies last", "pay more", "winner", "winning",
                        "you have been selected", "your income",
                        "verification required", "password expiry",
                        "expiration notice", "re:invoice", "missing invoice",
                        "action required", "suspicious activity", "important!",
                        "check out this", "don't miss", "exclusive",
                        "deal ending", "unbelievable", "claim now",
                        "claim your prize", "all-new", "one time only",
                        "hurry up", "now only", "new deals",
                        "on offer", "act fast"]
    emailOutcome = Outcome.ALLOWED.name
    threatType = ThreatType.NO_THREAT.value
    logMessage = "INBOUND: Email allowed."
    + " No suspicious words or attachments detected."

    # Keyword scanning
    for keyword in keywordBlacklist:
        if re.search(keyword, emailStr, re.IGNORECASE):
            emailOutcome = Outcome.DENIED.name
            exitCode = Outcome.DENIED.value
            threatType = ThreatType.SPAM_PHISHING.value
            logMessage = "INBOUND: Email denied."
            +" Suspicious word '%s' detected." % keyword
            break

    # Attachment scanning
    attachmentsDirectoryPath = f'/home/user/attachments-{randomChars}/'
    run(['ripmime', '-i', '-', '-d', attachmentsDirectoryPath],
        input=emailStr, text=True)  # Extract attachments
    scanResult = run(['clamdscan', '--stream', attachmentsDirectoryPath],
                     capture_output=True, text=True).stdout  # Scan attachments
    # Delete extracted attachments directory
    run(['rm', '-r', attachmentsDirectoryPath])
    infectedCount = re.findall(r'Infected files: (.+)',
                               scanResult)[0]  # Get infected attachment count

    if infectedCount != "0":
        emailOutcome = Outcome.DENIED.name
        exitCode = Outcome.DENIED.value
        threatType = ThreatType.VIRUS_MALWARE.value
        logMessage = "INBOUND: Email denied. Suspicious attachment detected."

    # Toggle off print() calls from utilities module to make room
    # for printing logMessage in postfix log
    sys.stdout = open(os.devnull, 'w')

    # Create and Add Email record
    emailCount = utilities.getEmailListCount('/opt/webapp/data/emails.bin')
    emailCount += 1
    emailId = emailCount

    # Create Email Object
    emailRecord = Email(emailId, emailToAddress, emailFromAddress,
                        emailSubject, emailBody, emailStr)

    # Get current email records and add Email record to list
    emailList = utilities.readFromBinaryFileToEmailList(
        '/opt/webapp/data/emails.bin')
    emailList.append(emailRecord)

    # Write the updated Email List to bin file
    utilities.writeToBinaryFileFromEmailList(
        '/opt/webapp/data/emails.bin', emailList)

    # Create and Add Log record
    logCount = utilities.getLogListCount('/opt/webapp/data/logs.bin')
    logCount += 1
    logId = logCount
    logDate = datetime.datetime.now().strftime("%d-%m-%Y")
    logTime = datetime.datetime.now().strftime("%H:%M")
    logTo = emailToAddress
    logFrom = emailFromAddress
    logSubject = emailSubject

    # Create Log object
    logRecord = Log(logId, logDate, logTime, logTo, logFrom,
                    logSubject, logMessage, threatType, emailOutcome)

    # Get current log records and add Log record to list
    logList = utilities.readFromBinaryFileToLogList(
        '/opt/webapp/data/logs.bin')
    logList.append(logRecord)

    # Write the updated Log List to bin file
    utilities.writeToBinaryFileFromLogList(
        '/opt/webapp/data/logs.bin', logList)

    # Toggle on print() calls so logMessage will print in postfix log
    sys.stdout = sys.__stdout__

print(logMessage)

sys.exit(exitCode)

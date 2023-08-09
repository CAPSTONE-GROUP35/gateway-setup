#!/usr/bin/env python

import sys
import re
from models.email import Email
from models.log import Log
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

# TODO: Write 'email' string variable to binary file & write its offsets and 'emailOutcome' variable to an index file

print(logMessage)

sys.exit(exitCode)

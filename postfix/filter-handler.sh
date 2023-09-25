#!/usr/bin/env bash

# Generate random string to facilitate synchronous filter service operations
randomChars=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)

# Location of the temporary file that will store the incoming email
temp_email_file=~/temp-email-file-${randomChars}.tmp

# Save the incoming email to the temporary file
cat > $temp_email_file

# Pass the temporary file into the content filter service. Also pass the name of the file as an argument
/etc/postfix/filter-service/filter-service.py "$temp_email_file" < $temp_email_file

# Retrieve the exit code of the content filter service (0 = No threat detected, 1 = Threat detected)
result=$?

# If no threat is detected, inject the email back into Postfix for delivery to the intended recipient
if [ $result = 0 ]; then
    echo "Forwarding email."
    /usr/sbin/sendmail -G -i $@ < $temp_email_file
else
    echo "NOT forwarding email."
fi

# Remove the temporary file. Comment out this line if you want to see what the full email looks like - the file will be owerwritten with each new email anyway.
rm $temp_email_file

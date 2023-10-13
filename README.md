# Overview
- There are 3x Raspberry Pi devices / servers on the same network each with static IP addresses.  
- The server hostnames should be external.test, gateway.test, internal.test  
- external.test and gateway.test should each have a user called 'user'.  
- internal.test should have a user called 'user1' (an organisation - can have multiple 'internal' users).  
- Emails sent from user@external.test to user1@internal.test will pass through the gateway server for filtering of malicious content. 
- Each email that passes through the gateway server for filtering is recorded and can be viewed via a web app on the gateway server (this includes both allowed and denied emails).
- Additionally, if the internal server were to send outbound emails to the external server:
    - A TLS connection is enforced for outbound emails in transit between the gateway server and the external server, thus encrypting the communication channel.  
    - Procedures for implementing PGP/MIME encryption are provided below. PGP/MIME encryption is when the email contents are encrypted by the sender with the intended recipient's public key, whereby the intended recipient is the only person who can decrypt the email with their private key (and an additional passphrase).  
    - Procedures for signing a email with PGP keys are provided below. Signing an email with PGP keys is a way to verify that the owner of the sending email address was the one who sent the email.  

# Gateway setup
## Configure Gateway server
- Set a static IP address by editing the /etc/dhcpcd.conf file. Uncomment and edit the 'Example static IP configuration' section.  
- Set the hostname: `sudo hostnamectl set-hostname gateway.test`  
- Create user: `sudo adduser user && sudo adduser user sudo`  
- Login as user.  
- Clone this repository somewhere inside the 'home' directory.  
- Make the setup.sh script executable: `chmod +x setup.sh`  
- Run the setup.sh script with elevated privileges: `sudo ./setup.sh`  
- Required software will install or reinstall. Choose the 'Internet Site' option, and enter 'gateway.test' as the domain.  
- The gateway should now be set up.  
- Run `sudo tail -f /var/log/mail.log` to view the live gateway Postfix log.

# System Testing
## Configure External server
- Set a static IP address by editing the /etc/dhcpcd.conf file. Uncomment and edit the 'Example static IP configuration' section.  
- Set the hostname: `sudo hostnamectl set-hostname external.test`  
- Create user: `sudo adduser user && sudo adduser user sudo`  
- Login as user.  
- Install Postfix: `sudo apt install postfix`. Choose the 'Internet Site' option, and enter 'external.test' as the domain.  
- Open Claws Mail and configure as follows: Email address should be user@external.test. Server type should be 'Local mbox file'. SMTP server address should be 'internal.test'.  

## Configure Internal server
- Set a static IP address by editing the /etc/dhcpcd.conf file. Uncomment and edit the 'Example static IP configuration' section.  
- Set the hostname: `sudo hostnamectl set-hostname internal.test`  
- Create user1: `sudo adduser user1 && sudo adduser user1 sudo`  
- Login as user1.   
- Install Postfix: `sudo apt install postfix`. Choose the 'Internet Site' option, and enter 'internal.test' as the domain.  
- Open Claws Mail and configure as follows:  Email address should be user1@internal.test. Server type should be 'Local mbox file'. SMTP server address should be 'external.test'.  

## Send emails from External server
- Login as 'user' on the external server.  
- Open Claws Mail and try sending emails to user1@internal.test

## Send emails from Internal server
- Login as 'user1' on the internal server.  
- Open Claws Mail and try sending emails to user@external.test

## PGP/MIME encryption procedure
### Configure External server
- Install Claws Mail plugins: `sudo apt install claws-mail-plugins`  
- In Claws Mail, nagivate to Configuration -> Plugins -> Load. Select: pgpmime.so and pgpcore.so. Click Open.  
- If you see the 'No PGP key found dialog' and are prompted to generate a new key pair, do it. Enter a passphrase, remember it. Copy the fingerprint. There is no need to export it to a key server. Close the Plugins window.  
- If you weren't prompted to generate a new key pair, close the Plugins window and navigate to Configuration -> Preferences for current account -> GPG. Click 'Generate a new key pair'. Enter a passphrase, remember it. Copy the fingerprint. There is no need to export it to a key server.  
- In a terminal, run: `gpg --list-keys`. The copied fingerprint belonging to user@external.test should be in the list of keys. If you forgot to copy it, copy it now.  
- Export the public key file by entering: `gpg --output ~/external-public-key.pub --export [FINGERPRINT]` where [FINGERPRINT] is the fingerprint that was copied.  
- For the purposes of this demo, email the public key file (external-public-key.pub) as an attachment to user1@internal.test. Note that in reality, the public key should be shared via a 'web of trust', whereby multiple parties are in agreement that the public key belongs to user@external.test.  

### Configure Internal server
- Check the inbox for the email from the external user containing their public key. Save the file to the ~ home directory.  
- In a terminal, import the public key into the local keyring by running: `gpg --import ~/external-public-key.pub`  
- Run `gpg --list-keys` to confirm that the public key belonging to user@external.test has been imported into the keyring.  
- Install Claws Mail plugins: `sudo apt install claws-mail-plugins`  
- In Claws Mail, nagivate to Configuration -> Plugins -> Load. Select: pgpmime.so and pgpcore.so. If you see the 'No PGP key found dialog' and are prompted to generate a new key pair, click no. Close the Plugins window.  
- Compose a new email addressed to user@external.test  
- Select Options -> Privacy System -> PGP/MIME. Select Options -> Encrypt  
- Click 'Send' to send the email. Claws Mail will match the email's 'To' address (user@external.test) to that address' public key that was imported into the keyring. Click through the 'Encryption warning'. Click through the 'Encrypt to user (user@external.test)' prompt. The email will then be sent.  

### External server
- The encrypted email should arrive in the external server's inbox. Open it and when prompted enter the passphrase that was chosen when creating the keys. The decrypted email contents should now be visible.    
- The external user may be prompted to enter their passphrase again to decrypt further emails during their session.  

## PGP signing
### Configure Internal server
- In Claws Mail, navigate to Configuration -> Preferences for current account -> GPG. 'Click 'Generate a new key pair'. Enter a passphrase, remember it. Copy the fingerprint. There is no need to export it to a key server.  Select 'Select key by your email address'. Click Apply and OK to save and exit.  
- In a terminal, run: `gpg --list-keys`. The copied fingerprint belonging to user1@internal.test should be in the list of keys. If you forgot to copy it, copy it now.  
- Export the public key file by entering: `gpg --output ~/internal-public-key.pub --export [FINGERPRINT]` where [FINGERPRINT] is the fingerprint that was copied.  
- For the purposes of this demo, email the public key file (internal-public-key.pub) as an attachment to user@external.test. Note that in reality, the public key should be shared via a 'web of trust', whereby multiple parties are in agreement that the public key belongs to user1@internal.test.  

### Configure External server
- Check the inbox for the email from the internal user containing their public key. Save the file to the ~ home directory.  
- In a terminal, import the public key into the local keyring by running: `gpg --import ~/internal-public-key.pub`  
- Run `gpg --list-keys` to confirm that the public key belonging to user1@internal.test has been imported into the keyring.  

### Internal server
- In Claws Mail, compose a new email addressed to user@external.test  
- Select Options -> Privacy System -> PGP/MIME. Select Options -> Sign  
- Click 'Send' to send the email. When prompted, enter the passphrase chosen earlier. This will sign the email with the user1@internal.test private key. The email will then be sent.  

### External server
- In Claws Mail, check the inbox for the signed email from user1@internal.test. Select the email.  
- At the bottom of the window, it should read 'This signature has not been checked'. Click the padlock next to this dialog. The text 'Good signature from user1 <user1@internal.test>' should appear, thus verifying that the email was signed with the user1@internal.test private key that pairs with the user1@internal.test public key in the external user's keyring.  

# Web App
## Accessing the web app
- Enter the 'webapp' directory and run the command 'flask run` to start the Web Application from a terminal, can be done from inside VS code terminal

## Running the web app
Once the Web App is running from the previous command, you can access the server in your browser either by clicking the link
127.0.0.1:5000/ in the terminal, or typing this address into your preferred browser address bar

# Utilities file for reading/adding/deleting Email/Log records
## Accessing utilities terminal menu
- How to access the utilities menu?
- Run 'python .\utilitiesMainMenu.py from 'gateway-setup\webapp\' folder OR
- Run the python script from VS code, must be in 'gateway-setup\webapp' folder in VS Code Terminal
- Option 1 -> Prints all email records saved to bin file in terminal
- Option 2 -> Prints all log records saved to bin file in terminal
- Option 3 -> Add 1 or more email records
- Option 4 -> Add 1 or more log records
- Option 5 -> Clear all email records
- Option 6 -> Clear all log records
- Option 7 -> Check user password hash
- Option 8 -> Exit the program

# DNS Server
## Configure DNS Server
- Install DNSmasq: `sudo apt install dnsmasq`
- Navigate to /etc/dnsmasq.conf to edit and uncomment 'domain-needed', 'bogus-priv' and 'no-resolv'
- To utilise Googles DNS server for their upstream nameservers, remove the line: '#server=/localnet/192.168.0.1'. Then replace it with: 'server=8.8.8.8' and 'server=8.8.4.4'
- To improve the performance on DNS lookups, uncomment and change the cache size line to: 'cache-size=1000'
- Save the file and restart DNSmasq: `sudo systemctl restart dnsmasq`
- Check the status of DNSmasq to ensure it is now active: `sudo systemctl status dnsmasq`

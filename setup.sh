#!/usr/bin/env bash

# Prompt user for server IP addresses
read -p "Enter internal server IP address: " INTERNAL_IP &&
read -p "Enter external server IP address: " EXTERNAL_IP &&

# Check if Postfix is installed
dpkg --status "postfix" &> /dev/null &&

# If Postfix is installed, uninstall it
if [ $? -eq 0 ]; then
    apt -y purge postfix
fi

# Check if Opdendkim is installed
dpkg --status "opendkim" &> /dev/null &&

# If Opdendkim is installed, uninstall it
if [ $? -eq 0 ]; then
    apt -y purge opendkim
fi

# Install packages
apt -y install postfix postfix-policyd-spf-python opendkim opendkim-tools ripmime clamav-daemon &&

# Copy files required for the destination relay to work
cp ./postfix/transport-maps ./postfix/relay-recipient-maps /etc/postfix &&

# Copy filter handler
cp ./postfix/filter-handler.sh /etc/postfix &&

# Copy filter service directory
cp -r ./postfix/filter-service /etc/postfix &&

# Make filter handler and filter service executable
chmod +x /etc/postfix/filter-handler.sh /etc/postfix/filter-service/filter-service.py &&

# Append additional settings to the main.cf config file
cat ./postfix/main.cf-additional-settings >> /etc/postfix/main.cf &&

# Append additional settings to the master.cf config file
cat ./postfix/master.cf-additional-settings >> /etc/postfix/master.cf &&

# Append additional settings to the opendkim.conf config file
cat ./postfix/opendkim.conf-additional-settings >> /etc/opendkim.conf &&

# Append additional settings to the opendkim config file
cat ./postfix/openkdim-default-additional-settings >> /etc/default/opendkim &&

# Set IP addresses
sed -i "s/<INTERNAL_SERVER_IP_ADDRESS>/$INTERNAL_IP/g" /etc/postfix/transport-maps /etc/opendkim.conf &&
sed -i "s/<EXTERNAL_SERVER_IP_ADDRESS>/$EXTERNAL_IP/g" /etc/postfix/transport-maps &&

# Generate opendkim key
opendkim-genkey -t -s mail -d internal.test &&

# Copy private key to postfix directory
cp mail.private /etc/postfix/dkim.key &&

# Set the relay maps
postmap /etc/postfix/transport-maps &&
postmap /etc/postfix/relay-recipient-maps &&

# Reload Postfix
postfix reload &&

# Start opendkim
service opendkim start &&

# Copy webapp to opt directory
cp -r ./webapp /opt &&

# Set ownership to write to binary files
chown -R user /opt/webapp/data/ &&

# Install flask packages
pip install flask_sqlalchemy flask_login &&

# Enable and start clamav daemon
systemctl enable clamav-daemon &&
systemctl start clamav-daemon &&

# Reboot
for i in {10..1}
do
    echo "Rebooting in $i"
    sleep 1
done

reboot

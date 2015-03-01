#!/bin/bash

cp -f wifi-check.sh /usr/bin/wifi-check.sh
cp -f wifi_check.py /usr/bin/wifi_check.py
cp -f wifi-check.service /lib/systemd/system/wifi-check.service
cp -f wifi-reset.sh /usr/bin/wifi-reset.sh
cp -f routerPing.sh /usr/bin/routerPing.sh
chmod +x /usr/bin/routerPing.sh
chmod +x /usr/bin/wifi-reset.sh
chmod +x /usr/bin/wifi-check.sh

cp -f emailIP.sh /usr/bin/emailIP.sh
cp -f emailSendTest.py /usr/bin/emailSendTest.py
cp -f emailIP.service /lib/systemd/system/emailIP.service 

systemctl  daemon-reload
systemctl enable wifi-check.service
systemctl enable emailIP.service
systemctl start wifi-check.service
systemctl start emailIP.service

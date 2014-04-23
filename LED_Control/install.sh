#!/bin/bash

cp -f TurnOffLeds.sh /usr/bin/TurnOffLeds.sh
cp -f LEDOff.service /lib/systemd/system/LEDOff.service
chmod +x /usr/bin/TurnOffLeds.sh

systemctl daemon-reload
systemctl enable LEDOff.service
systemctl start LEDOff.service

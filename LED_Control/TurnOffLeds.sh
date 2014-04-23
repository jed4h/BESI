#!/bin/bash
# Turn off all user LEDS

echo none > /sys/class/leds/beaglebone:green:usr0/trigger
echo none > /sys/class/leds/beaglebone:green:usr1/trigger
echo none > /sys/class/leds/beaglebone:green:usr2/trigger
echo none > /sys/class/leds/beaglebone:green:usr3/trigger

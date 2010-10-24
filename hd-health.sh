#!/bin/sh
echo "/dev/sda1"
sudo hddtemp /dev/sda1
sudo smartctl --health /dev/sda1 | tail -1
echo "/dev/sdb2"
sudo hddtemp /dev/sdb2
sudo smartctl --health /dev/sdb2 | tail -1

#!/bin/sh
echo "/dev/sda1"
sudo hddtemp /dev/sda1
sudo smartctl --health /dev/sda1 | tail -1
echo "/dev/sdb1"
sudo hddtemp /dev/sdb1
sudo smartctl --health /dev/sdb1 | tail -1

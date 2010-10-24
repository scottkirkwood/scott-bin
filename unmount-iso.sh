#!/bin/bash
#
for I in "$*"
do
foo=`gksudo -u root -k -m "enter your password for root terminal
access" /bin/echo "got r00t?"`

sudo umount "$I" && zenity --info --text "Successfully unmounted /media/$I/" && sudo rmdir "/media/$I/"
done
done
exit0
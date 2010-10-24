#!/bin/bash
#
# nautilus-mount-iso

gksudo -u root -k /bin/echo "got r00t?"

sudo mkdir /media/"$*"

if sudo mount -o loop -t iso9660 "$*" /media/"$*"
then
        if zenity --question --title "ISO Mounter" --text "$* Successfully Mounted.
        
        Open Volume?"
        then
                nautilus /media/"$*" --no-desktop
        fi
        exit 0
else
        sudo rmdir /media/"$*"
        zenity --error --title "ISO Mounter" --text "Cannot mount $*!"
        exit 1
fi
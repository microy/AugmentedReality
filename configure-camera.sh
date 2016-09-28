#! /bin/sh

#
# Configure the USB camera
#

# Fix power line frequency
uvcdynctrl -v -d video0 --set='Power Line Frequency' 1

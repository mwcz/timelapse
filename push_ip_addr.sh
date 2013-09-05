#!/bin/bash

LPATH="/home/pi/timelapse/"
cd $LPATH

# since I only gave my app Image permissions in dropbox... I'm sillily pushing
# an image named with the IP address the raspi was given, so I can check
# dropbox and then ssh into it.
IP=$(hostname -I)
cp IP_ADDR.jpg "$(echo $IP).jpg"
python ./db.py put "$(echo $IP).jpg" pictures/timelapse/"$(echo $IP).jpg"
rm "$(echo $IP).jpg"

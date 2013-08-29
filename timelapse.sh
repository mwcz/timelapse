#!/bin/bash

SAVE_PATH=$HOME'/Pictures/timelapse/testing/'
SAVE_EXT='.jpg'
CAPTURE_CMD='fswebcam'

function capture {
    $(echo "$CAPTURE_CMD $SAVE_PATH$($1)$SAVE_EXT")
}

while true
do

    # take the picture
    capture 'date +%s'

    # wait
    sleep 1s

    # push the file to dropbox
    #db.py put ~/Pictures/timelapse/testing/$(date +%s).jpg Pictures/timelapse/testing/$(date +%s).jpg

    # wait for the file to show up in dropbox before continuing
    #while [true]
    #do
        #foo=$(db.py search Pictures/timelapse/testing/$(date +%s).jpg)
        #if [[ foo -eq 'true' ]]; then
            #statements
        #fi
        #sleep 1s
    #done

    # delete the file
    #rm ~/Pictures/timelapse/testing/$(date +%s).jpg

done


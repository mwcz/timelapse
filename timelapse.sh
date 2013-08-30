#!/bin/bash

SAVE_PATH_LOCAL='imgs/'
SAVE_PATH_REMOTE='pictures/timelapse/testing/'
SAVE_EXT='.jpg'
CAPTURE_CMD='fswebcam'
DELAY='5s'

function capture {
    $CAPTURE_CMD $1
}

while true
do

    # generate image named based on epoch time
    FILENAME=$(date +%s)$SAVE_EXT

    # take the picture
    capture $SAVE_PATH_LOCAL$FILENAME

    # wait
    sleep $DELAY

    # push the file to dropbox
    python db.py put $SAVE_PATH_LOCAL$FILENAME $SAVE_PATH_REMOTE$FILENAME

    # delete the local file
    rm $SAVE_PATH_LOCAL$FILENAME

done

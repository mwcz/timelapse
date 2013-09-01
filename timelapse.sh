#!/bin/bash

SERIES_NAME=$1
SAVE_PATH_LOCAL='imgs/'
SAVE_PATH_REMOTE='pictures/timelapse/'$SERIES_NAME'/'
SAVE_EXT='.jpg'
DELAY='5s'
source capture.sh # pull in $CAPTURE_CMD

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

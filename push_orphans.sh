#!/bin/bash

for dir in `ls imgs`; do

    # If it's a dir, then its a timelapse series, so get the jpgs and
    # push them to dropbox
    if [[ -d "imgs/$dir" ]]; then
        # For each orphaned image
        for fn in `ls imgs/$dir/*.jpg`; do

            FN=`basename $fn`

            # if the image already exists in dropbox, don't upload it
            # if it doesn't exist, upload it
            EXIST=$(python db.py search $FN)
            if [[ $EXIST == "/pictures/timelapse/$dir/$FN" ]]; then
                echo already exists $fn
            else
                python db.py put imgs/$dir/$FN pictures/timelapse/$dir/$FN
                echo pushed\ \ \ \ \ \ \ \ \ $fn
            fi

        done
        rm imgs/$dir/*.jpg
        rmdir imgs/$dir
    fi
done

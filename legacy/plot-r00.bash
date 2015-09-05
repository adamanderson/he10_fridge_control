#!/bin/bash

COUNTER=0
while [ $COUNTER -lt 100000 ]; do

rm -f r00-480.data
tail -480 r00.data > r00-480.data

./r00.py

# cp r00.png ~/Desktop/GoogleDriveHN/r00.png
# cp r00.png /home/spt3g/Desktop/Google\ Drive/r00.png
mv r00.png ./plots

sleep 15

done

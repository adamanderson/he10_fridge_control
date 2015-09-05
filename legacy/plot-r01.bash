#!/bin/bash

COUNTER=0
while [ $COUNTER -lt 100000 ]; do

rm -f r01-480.data
tail -480 r01.data > r01-480.data 
./r01.py
# cp r01.png ~/Desktop/GoogleDriveHN/r01.png
# cp r01.png /home/spt3g/Google\ Drive/r01.png
mv r01.png ./plots

sleep 15

done

#!/bin/bash

COUNTER=0
while [ $COUNTER -lt 100000 ]; do

rm -f eth2-480.data
tail -480 eth2.data > eth2-480.data

./eth2.py


# cp eth2.png ~/Desktop/GoogleDriveHN/eth2.png
# cp eth2.png /home/spt3g/Google\ Drive/eth2.png
mv eth2.png ./plots

sleep 15

done

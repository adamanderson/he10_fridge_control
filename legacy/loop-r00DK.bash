#!/bin/bash
# set the curve to DT-670
./arduino-serial -q -p /dev/ttyr00 -S "INCRV 1 21" -F 
./arduino-serial -q -p /dev/ttyr00 -S "INCRV 2 22" -F
./arduino-serial -q -p /dev/ttyr00 -S "INCRV 3 23" -F
./arduino-serial -q -p /dev/ttyr00 -S "INCRV 4 24" -F
./arduino-serial -q -p /dev/ttyr00 -S "INCRV 5 25" -F
./arduino-serial -q -p /dev/ttyr00 -S "INCRV 6 26" -F
./arduino-serial -q -p /dev/ttyr00 -S "INCRV 7 27" -F
./arduino-serial -q -p /dev/ttyr00 -S "INCRV 8 28" -F

# collect data 
COUNTER=0
while [ $COUNTER -lt 100000 ]; do
  	./arduino-serial -q -p /dev/ttyr00 -S "KRDG?" -r  -F
  	sleep 15  
	let COUNTER=COUNTER+1
done

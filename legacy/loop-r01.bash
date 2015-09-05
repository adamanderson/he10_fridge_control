#!/bin/bash
# set the curve to DT-670
./arduino-serial -q -p /dev/ttyr01 -S "INCRV 1 4 " -F 
./arduino-serial -q -p /dev/ttyr01 -S "INCRV 2 4 " -F
./arduino-serial -q -p /dev/ttyr01 -S "INCRV 3 4 " -F
./arduino-serial -q -p /dev/ttyr01 -S "INCRV 4 4 " -F
./arduino-serial -q -p /dev/ttyr01 -S "INCRV 5 4 " -F
./arduino-serial -q -p /dev/ttyr01 -S "INCRV 6 4 " -F
./arduino-serial -q -p /dev/ttyr01 -S "INCRV 7 4 " -F
./arduino-serial -q -p /dev/ttyr01 -S "INCRV 8 4 " -F

# collect data 
COUNTER=0
while [ $COUNTER -lt 100000 ]; do
  	./arduino-serial -q -p /dev/ttyr01 -S "KRDG?" -r  -F
  	sleep 15  
	let COUNTER=COUNTER+1
done

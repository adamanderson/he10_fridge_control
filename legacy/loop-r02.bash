#!/bin/bash

# read the agilent 3631A voltages and currents on ttyr02

# HHN:  August 15, 2015. 
# First put the Agilent into Remote Mode.  So the Front Panel is disabled
./arduino-serial -q -p /dev/ttyr02 -S "SYST:REM" -r -F  >/dev/null

COUNTER=0
while [ $COUNTER -lt 100000 ]; do
        rm temp-r02-p25.out
        rm temp-r02-n25.out
        rm temp-r02-p6.out
        rm temp-r02-ip25.out
        rm temp-r02-in25.out
        rm temp-r02-ip6.out
  	./arduino-serial -q -p /dev/ttyr02 -S "MEAS:VOLT:DC? P25V" -r  -F  > temp-r02-p25.out
  	./arduino-serial -q -p /dev/ttyr02 -S "MEAS:VOLT:DC? N25V" -r  -F  > temp-r02-n25.out
  	./arduino-serial -q -p /dev/ttyr02 -S "MEAS:VOLT:DC? P6V" -r  -F  >  temp-r02-p6.out
  	./arduino-serial -q -p /dev/ttyr02 -S "MEAS:CURR:DC? P25V" -r  -F  > temp-r02-ip25.out
  	./arduino-serial -q -p /dev/ttyr02 -S "MEAS:CURR:DC? N25V" -r  -F  > temp-r02-in25.out
  	./arduino-serial -q -p /dev/ttyr02 -S "MEAS:CURR:DC? P6V" -r  -F >  temp-r02-ip6.out

	# HHN: August 16th, 2015
        # fix the weird problem of the hidden carriage return
        dos2unix -q temp-r02-p25.out  
        dos2unix -q temp-r02-n25.out  
        dos2unix -q temp-r02-p6.out  
        dos2unix -q temp-r02-ip25.out  
        dos2unix -q temp-r02-in25.out  
        dos2unix -q temp-r02-ip6.out  
        year=$(cat temp-r02-p25.out | awk '{print $1}' )         
        month=$(cat temp-r02-p25.out | awk '{print $2}' )         
        day=$(cat temp-r02-p25.out | awk '{print $3}' )         
        hour=$(cat temp-r02-p25.out | awk '{print $4}' )         
        min=$(cat temp-r02-p25.out | awk '{print $5}' )         
        sec=$(cat temp-r02-p25.out | awk '{print $6}' )         

        p25v=$(cat temp-r02-p25.out | awk '{print $7}' ) 
        n25v=$(cat temp-r02-n25.out | awk '{print $7}' ) 
        p6v=$(cat temp-r02-p6.out | awk '{print $7}' ) 
        ip25v=$(cat temp-r02-ip25.out | awk '{print $7}' ) 
        in25v=$(cat temp-r02-in25.out | awk '{print $7}' ) 
        ip6v=$(cat temp-r02-ip6.out | awk '{print $7}' ) 
        echo $year $month $day $hour $min $sec $p25v $n25v $p6v $ip25v $in25v $ip6v

  	sleep 30  

	let COUNTER=COUNTER+1
done

#!/bin/bash

# read the agilent 3631A voltages and currents on ttyr03

# HHN: August 15th 2015
# Put the Agilent into remote mode, so that the front panel is disabled.
./arduino-serial -q -p /dev/ttyr03 -S "SYST:REM" -r -F  >/dev/null 

COUNTER=0
while [ $COUNTER -lt 100000 ]; do
        rm temp-r03-p25.out
        rm temp-r03-n25.out
        rm temp-r03-p6.out
        rm temp-r03-ip25.out
        rm temp-r03-in25.out
        rm temp-r03-ip6.out
  	./arduino-serial -q -p /dev/ttyr03 -S "MEAS:VOLT:DC? P25V" -r  -F  > temp-r03-p25.out
  	./arduino-serial -q -p /dev/ttyr03 -S "MEAS:VOLT:DC? N25V" -r  -F  > temp-r03-n25.out
  	./arduino-serial -q -p /dev/ttyr03 -S "MEAS:VOLT:DC? P6V" -r  -F  >  temp-r03-p6.out
  	./arduino-serial -q -p /dev/ttyr03 -S "MEAS:CURR:DC? P25V" -r  -F  > temp-r03-ip25.out
  	./arduino-serial -q -p /dev/ttyr03 -S "MEAS:CURR:DC? N25V" -r  -F  > temp-r03-in25.out
  	./arduino-serial -q -p /dev/ttyr03 -S "MEAS:CURR:DC? P6V" -r  -F  >  temp-r03-ip6.out

	# HHN: August 16th, 2015
        # fix the weird problem of the hidden carriage return
        dos2unix -q temp-r03-p25.out  
        dos2unix -q temp-r03-n25.out  
        dos2unix -q temp-r03-p6.out  
        dos2unix -q temp-r03-ip25.out  
        dos2unix -q temp-r03-in25.out  
        dos2unix -q temp-r03-ip6.out  

        year=$(cat temp-r03-p25.out | awk '{print $1}' )         
        month=$(cat temp-r03-p25.out | awk '{print $2}' )         
        day=$(cat temp-r03-p25.out | awk '{print $3}' )         
        hour=$(cat temp-r03-p25.out | awk '{print $4}' )         
        min=$(cat temp-r03-p25.out | awk '{print $5}' )         
        sec=$(cat temp-r03-p25.out | awk '{print $6}' )         

        p25v=$(cat temp-r03-p25.out | awk '{print $7}' ) 
        n25v=$(cat temp-r03-n25.out | awk '{print $7}' ) 
        p6v=$(cat temp-r03-p6.out | awk '{print $7}' ) 
        ip25v=$(cat temp-r03-ip25.out | awk '{print $7}' ) 
        in25v=$(cat temp-r03-in25.out | awk '{print $7}' ) 
        ip6v=$(cat temp-r03-ip6.out | awk '{print $7}' ) 

        echo $year $month $day $hour $min $sec $p25v $n25v $p6v $ip25v $in25v $ip6v
  	sleep 30  

	let COUNTER=COUNTER+1
done

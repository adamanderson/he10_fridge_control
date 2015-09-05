#!/bin/bash

#  Hogan Nguyen:  May 30th, 2015

# simple script to collect data on Lake shore 350 using TCP/IP socket communication

# for this to work, must check that eth1 is up and running
# to check, type ifconfig

# to get eth1 up, type: ifup eth1

# the port of the Lakeshore 350 is always 7777

# the ip address of the lakeshore 350 is 192.168.0.12 by default.

# format to run is:

# client  ip-address  port-number

COUNTER=0
while [ $COUNTER -lt 100000 ]; do
  	~/Desktop/ls350/client 192.168.0.12 7777 <<EOF
KRDG? 0 
EOF
  	sleep 15
	let COUNTER=COUNTER+1
done

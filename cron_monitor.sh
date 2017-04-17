#!/bin/bash
# cron_monitor.sh - Bash script to run and sustain MLBell monitor.py program (that monitors a specific MLB game). This script is intended to be run from a CRONTAB job. It sets a flag, and repeatedly calls mlbell_monitor.py until it exits cleanly, then clears the flag.

# Set up defaults...
TEAM=PHI
DIR=/home/mlb/MLBell
LOGFILE=monitor.log
MONITOR=HR #HR=homeruns, R=runs, S=any scoring by either team
# $$ is the PID for this script
FLAGFILE="/tmp/cron_monitor_$$.flg"

# Process command line options...
while getopts t:d:m: option
do
        case "${option}"
        in
                t) TEAM=${OPTARG};;
                d) DIR=${OPTARG};;
                m) MONITOR=${OPTARG};;
        esac
done

cd $DIR
touch $FLAGFILE
echo "`date +%H:%M:%S` : Starting cron_monitor.sh for " $TEAM " (" $MONITOR ")" >> $LOGFILE
# Play Ball! sound effect...
python play_start.py

# While flag is set, start monitor...
while [ -e $FLAGFILE ]
do
	echo "`date +%H:%M:%S` : Starting mlbell_monitor.py -t" $TEAM " -m" $MONITOR  >> $LOGFILE	
	./mlbell_monitor.py -t $TEAM -m $MONITOR &>> $LOGFILE 
	if [ $? -eq 0 ]; then #Exiting monitoring cleanly... 
		echo "`date +%H:%M:%S` : Ending cron_monitor.sh" >> $LOGFILE
		rm $FLAGFILE
        # Play end of game sound effect...
        python play_end.py
		exit 0
	fi
done

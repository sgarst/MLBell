#!/bin/bash
# cron_monitor.sh - Bash script to run and sustain MLBell monitor.py program (that monitors a specific MLB game). This script is intended to be run from a CRONTAB job.
# Set up defaults...
TEAM=PHI
DIR=/home/mlb/MLBell
LOGFILE=monitor.log
FLAGFILE=/tmp/cron_monitor.flg

# Process command line options...
while getopts t:d: option
do
        case "${option}"
        in
                t) TEAM=${OPTARG};;
                d) DIR=${OPTARG};;
        esac
done

cd $DIR
touch $FLAGFILE
echo "`date +%H:%M:%S` : Starting cron_monitor.sh for " $TEAM >> $LOGFILE

# While flag is set, start monitor...
while [ -e $FLAGFILE ]
do
	echo "`date +%H:%M:%S` : Starting mlbell_monitor.py -t" $TEAM  >> $LOGFILE	
	./mlbell_monitor.py -t $TEAM &>> $LOGFILE 
	if [ $? -eq 0 ]; then #Exiting monitoring cleanly... 
		echo "`date +%H:%M:%S` : Ending cron_monitor.sh" >> $LOGFILE
		rm $FLAGFILE
		exit 0
	fi
done

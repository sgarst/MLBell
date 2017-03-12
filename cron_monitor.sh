#!/bin/bash
# cron_monitor.sh - Bash script to run and sustain MLBell monitor.py program (that monitors a specific MLB game). This script is intended to be run from a CRONTAB job.

TEAM=COL
LOGFILE=monitor.log
FLAGFILE=/tmp/cron_monitor.flg

cd /home/mlb/MLBell
touch $FLAGFILE
echo "`date +%H:%M:%S` : Starting cron_monitor.sh" >> $LOGFILE

# while flag is set, start monitor...
# run monitor.py -t PHI... 
while [ -e $FLAGFILE ]
do
	echo "`date +%H:%M:%S` : Starting MM2..." >> $LOGFILE	
	./mlbell_monitor.py -t $TEAM &>> $LOGFILE 
#	./test.sh >> $LOGFILE 2>&1
	if [ $? -eq 0 ]; then #Exiting monitoring cleanly... 
		echo "`date +%H:%M:%S` : Ending cron_monitor.sh" >> $LOGFILE
		rm $FLAGFILE
		exit 0
	fi
done

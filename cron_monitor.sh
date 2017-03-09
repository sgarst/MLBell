#!/bin/bash
# cron_monitor.sh - Bash script to run and sustain MLBell monitor.py program (that monitors a specific MLB game). This script is intended to be run from a CRONTAB job.

LOGFILE=monitor.log
FLAGFILE=/tmp/cron_monitor.flg

cd ~/Dev/MLBell
touch $FLAGFILE
echo "`date +%H:%M:%S` : Starting cron_monitor.sh" >> $LOGFILE

#if flag is set, then last run aborted, so run again
# run monitor.py -t PHI... 
while [ -e $FLAGFILE ]
do
	echo "`date +%H:%M:%S` : Starting MM2..." >> $LOGFILE	
#	./MM2.py -t OAK >> $LOGFILE 2>&1
	./test.sh >> $LOGFILE 2>&1
	if [ $? -eq 0 ]; then
		echo "`date +%H:%M:%S` : Ending cron_monitor.sh" >> $LOGFILE
		rm $FLAGFILE
		exit 0
	fi
done

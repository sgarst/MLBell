#!/bin/bash
# status.sh - script to dump status on mlbell...
# SWGarst 4/5/2017

echo "Crontab:"
crontab -l | sed '/^\s*$/d'

if ps -e | grep -q monitor
then
   echo -e "\nPS:"
   ps -e | grep monitor
else 
   echo -e "\nNo monitor running!"
fi

if test -n "$(find /tmp -name 'cron*' -print -quit)"
then
    echo -e "\nCron flag files:"
    ls -l /tmp/cron*
else
    echo "No cron flags found!"
fi
echo -e "\n"


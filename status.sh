#!/bin/bash
# status.sh - script to dump status on mlbell...
# SWGarst 4/5/2017

echo "Crontab:"
crontab -l
echo -e "\nPS:"
ps -e | grep monitor
if test -n "$(find /tmp -name 'cron*' -print -quit)"
then 
   echo -e "\nCron flags:" 
   ls -l /tmp/cron*
else 
   echo "No cron flags found.."
fi


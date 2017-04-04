#!/bin/bash
# mlbell_status.sh - script to dump status on mlbell...
# 3/28/2017

echo "Crontab:"
crontab -l
echo -e "\nPS:"
if ps -e | grep -q monitor
then ps -e | grep monitor
else echo "No monitor running!"
fi
echo -e "\nFlag files:"
if test -n "$(find /tmp -name 'cron*' -print -quit)"
then
    ls -l /tmp/cron*
else
    echo "No cron file(s) found!"
fi


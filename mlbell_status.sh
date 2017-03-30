#!/bin/bash
# mlbell_status.sh - script to dump status on mlbell...
# 3/28/2017

echo "Crontab:"
crontab -l
echo "PS:"
ps -e | grep monitor
echo "Flag files:"
ls /tmp/cron*
echo "Monitor.log:"
tail monitor.log


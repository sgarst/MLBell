#!/usr/bin/python
# mlbell_schedule.py - determine if there are any games today, and if so set up monitoring.

import sys, getopt, time, datetime, re
from crontab import CronTab
import requests
import xml.etree.cElementTree as ET

class Game:
    def __init__(self, gameuri, status, inning, home, away, date):
        self.gameuri = gameuri
        self.status = status
        self.inninv = inning
        self.lastupdate = time.strftime("%H:%M:%S")
        self.home = home
        self.away = away
        self.date = date
        self.homeR = 0 # Runs for home team
        self.awayR = 0 # Runs for away team
        self.homeHR = 0 # Homeruns for home team
        self.awayHR = 0 # Homeruns for away team

def main(argv):
# Set defaults...
   team = 'PHI'
   monitor = 'HR'
   gamedate=datetime.date.today()
   try:
      opts, args = getopt.getopt(argv,"ht:m:d:",["team=", "date=", "monitor="])
   except getopt.GetoptError:
      print 'mlbell_schedule.py -t <team>  -d <date YYYY-MM-DD> -m <monitor HR/R/S>'
      sys.exit(2)
   for opt, arg in opts:
      if opt in ('-h','--help'):
         print 'mlbell_schedule.py -t <team>  -d <date YYYY-MM-DD> -m <monitor HR/R/S>'
         sys.exit()
      elif opt in ("-t", "--team"):
          #Not validating teams...
         team = arg.upper()
      elif opt in ("-m", "--monitor"):
         if arg.upper() in ("S", "R", "HR"):
            monitor = arg.upper()
      elif opt in ("-d", "--date"):
          #validating format... but not dates (like April 31st)
          if re.match("^(20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$", arg):
              gamedate=datetime.datetime.strptime(arg,'%Y-%m-%d')
   
   return team, gamedate, monitor

def get_game(team, gamedate):
# Build a list of all games that "team" is playing on "gamedate"
# Reformat gamedate to mlb's url scheme...
    datestr=gamedate.strftime('year_%Y/month_%m/day_%d/')
    url = "http://gd2.mlb.com/components/game/mlb/" + datestr + "epg.xml"
    games = []
    try:
        req = requests.get(url, timeout=20)
    except requests.RequestException as e:
        print 'get_game request error: ', e
    else:
        root = ET.fromstring(req.text)
    
    #Now, parse epg.xml, looking for any games with "Team"
    for g in (root.findall('game/[@home_name_abbrev="{}"]'.format(team)) + root.findall('game/[@away_name_abbrev="{}"]'.format(team))):
        dt = g.get('time_date') + " " + g.get('ampm')
        gamedate = datetime.datetime.strptime(dt, '%Y/%m/%d %I:%M %p')
        game = Game(g.get('game_data_directory'), g.get('status'), g.get('inning'), g.get('home_name_abbrev'), g.get('away_name_abbrev'), gamedate)
        games.append(game)
    return games

### MAIN ###
if __name__ == "__main__":
    t,d,m = main(sys.argv[1:])
    print '%s : Starting mlbell_schedule with team %s on %s (Monitor: %s).' \
        %(time.strftime("%D %H:%M:%S"), t, d.strftime('%m/%d/%Y'), m)
    games = get_game(t,d)
    if not (games):
        print '%s: No games for %s on %s.' %(time.strftime("%D %H:%M:%S"), t, d.strftime('%m/%d/%Y'))
    # SETUP crontab
    cron = CronTab(user=True)
    # FIRST, clean out any crontabs from yesterday...
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yesterdaycron = '%s %s' %(yesterday.day,yesterday.month)
    for job in cron:
        jobstr = str(job)
        if (jobstr.find(yesterdaycron) > 0):
            print '%s : Removing crontab %s' \
             %(time.strftime("%D %H:%M:%S"),job.command)
            cron.remove (job)
    cron.write()
    # Now, write any games to monitor today...
    for game in games:
        # IF STATUS = FINAL, THEN exit
        if (game.status == "Final"):
            print '%s : Game over (%s vs %s at %s)' \
                %(time.strftime("%D %H:%M:%S"), game.home, game.away, game.date.strftime('%I:%M %p'))
        # ELSE IF GAME In Progress/WarmingUp... fire off monitoring
        elif (game.status in ["In Progress","WarmingUp"]):
            print '%s : Game in progress (%s vs %s at %s)' \
                 %(time.strftime("%D %H:%M:%S"), game.home, \
                game.away, game.date.strftime('%I:%M %p'))
        # ELSE CREATE NEW CRONTAB ENTRY
        else:
            print '%s : Adding crontab for %s vs %s, on %s' \
             %(time.strftime("%D %H:%M:%S"), game.home, game.away, game.date.strftime('%m/%d/%Y %I:%M %p') )
            cmd = "/home/mlb/MLBell/cron_monitor.sh -t" + t \
                + " -m" + m + " >> /home/mlb/MLBell/monitor.log 2>&1"
            cmt = "%s vs %s, %s" %(game.home, game.away, game.date.strftime('%I:%M %p') )
            job = cron.new(command=cmd, comment=cmt)
            job.setall(game.date)
            job.enable
            cron.write()

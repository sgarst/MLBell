#!/usr/bin/python
# mlbell_schedule.py - determine if there are any games today, and if so set up monitoring.

import sys, getopt, time, datetime
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
   datestr=datetime.date.today().strftime('%Y-%m-%d')
   try:
      opts, args = getopt.getopt(argv,"ht:m:d:",["team=", "monitor=", "date="])
   except getopt.GetoptError:
      print 'mlbell_schedule.py -t <team> -m <monitor HR/R/S> \
        -d <date YYYY-MM-DD>'
      sys.exit(2)
   for opt, arg in opts:
      if opt in ('-h','--help'):
        print 'mlbell_schedule.py -t <team> -m <monitor HR/R/S> \
            -d <date YYYY-MM-DD>'
        sys.exit()
      elif opt in ("-t", "--team"):
         team = arg.upper()
      elif opt in ("-m", "--monitor"):
         if arg.upper() in ("S", "R", "HR"):
            monitor = arg.upper()
      elif opt in ("-d", "--date"):
          datestr = arg
          # REGEX for date format YYYY-MM-DD: ^(20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$
          # if re.match("^(20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$", datestr):
   return team, monitor, datestr

def get_game(team, datestr = time.strftime("year_%Y/month_%m/day_%d/") ):
# Build a list of all games that "team" is playing "datestr" (or today, if datestr not passed in)

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
        gdate = g.get('time_date') + ' ' + g.get('ampm') + ' (' + g.get('time_zone') + ')' 
        game = Game(g.get('game_data_directory'), g.get('status'), g.get('inning'), g.get('home_name_abbrev'), g.get('away_name_abbrev'), gdate)
        games.append(game)
    return games

### MAIN ###      
if __name__ == "__main__": 
    t,m,d = main(sys.argv[1:])
    print '%s : Starting mlbell_schedule with team %s on %s (Monitoring: %s).' \
        %(time.strftime("%D %H:%M:%S"), t, d, m)
    #convert date to proper format
    datestr = 'year_{}/month_{}/day_{}/'.format(d[0:4], d[5:7],d[8:10])
    games = get_game(t,datestr)

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
                %(time.strftime("%D %H:%M:%S"), game.home, game.away, game.date)
        # ELSE IF GAME In Progress/WarmingUp... fire off monitoring 
        elif (game.status in ["In Progress","WarmingUp"]): 
            print '%s : Game in progress (%s vs %s at %s)' \
                 %(time.strftime("%D %H:%M:%S"), game.home, \
                game.away, game.date)
        # ELSE CREATE NEW CRONTAB ENTRY
        else:
            gamemin = int(game.date[13:15])
            gamehour = int(game.date[11:12])
            if (game.date[16:18] == "PM"):
                gamehour = gamehour + 12
            gamemonth = int(game.date[5:7])
            gameday = int(game.date[8:10])

            print '%s : Adding crontab for %s vs %s, on %i/%i at %i:%i' \
             %(time.strftime("%D %H:%M:%S"), game.home, game.away, gamemonth, \
             gameday, gamehour, gamemin)
            cmd = "/home/mlb/MLBell/cron_monitor.sh -t" + t \
                + " -m" + m + " >> /home/mlb/MLBell/monitor.log 2>&1"
            # Clean up comment to show 'real' time/date
            cmt = "%s vs %s, %i/%i %i:%i" %(game.home, game.away, gamemonth, \
             gameday, gamehour, gamemin)
            job = cron.new(command=cmd, comment=cmt)
            job.minute.on(gamemin)
            job.hour.on(gamehour)
            job.day.on(gameday)
            job.month.on(gamemonth)
            job.enable
            cron.write()

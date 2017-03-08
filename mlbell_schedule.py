#!/usr/bin/python
# mlbell_schedule.py - determine if there are any games today, and if so set up monitoring.

import sys, getopt, time
import shutil
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
   team = ''
   gameuri = ''
   datestr=''
   try:
      opts, args = getopt.getopt(argv,"ht:d:",["team=","date="])
   except getopt.GetoptError:
      print 'mlbell_schedule.py -t <team> -d <date YYYY-MM-DD>'
      sys.exit(2)
   for opt, arg in opts:
      if opt in ('-h','--help'):
         print 'mlbell_schedule.py -t <team> -d <date YYYY-MM-DD>'
         sys.exit()
      elif opt in ("-t", "--team"):
         team = arg.upper()
      elif opt in ("-d", "--date"):
          datestr = datetime.date.today().strftime('%Y-%m-%d')
   return team

def parse_game(url, team): #Parse miniscoreboard.xml
    try:
        req = requests.get(url, timeout=10)
    except req.RequestException as e:
        print 'parse_game request error: ', e
    else:
        root = ET.fromstring(req.text)

    #### LOCAL FILE TEST ####
    # root = ET.parse(open("miniscoreboard.xml", "r"))
    
    status = root.find('game_status[@status]').get('status')
    date = root.get('id')[0:9]
    runs = root.find('linescore/r')
    homeruns = root.find('linescore/hr')
    inning = root.find('game_status[@inning]').get('inning')
    
    # Create game object, return
    g = Game(url, status, inning, root.get('home_name_abbrev'), root.get('away_name_abbrev'), date)
    g.lastupdate = time.strftime("%H:%M:%S")
    g.inning = inning
    g.homeR = runs.get('home')
    g.awayR = runs.get('away')
    g.homeHR = homeruns.get('home')
    g.awayHR = homeruns.get('away')
    return(g)

def get_game(team, datestr = time.strftime("year_%Y/month_%m/day_%d/") ):
# Build a list of all games that "team" is playing "datestr" (or today, if datestr not passed in)
    url = "http://gd2.mlb.com/components/game/mlb/" + datestr + "epg.xml"
    games = []
    try:
        req = requests.get(url, timeout=10)
    except req.RequestException as e:
        print 'get_game request error: ', e
    else:
        root = ET.fromstring(req.text)
        
    #### LOCAL FILE TEST ####
    #root = /.parse(open("epg2.xml", "r"))
    #### END LOCAL FILE TEST ####
    
    #Now, parse epg.xml, looking for any games with "Team"
    for g in (root.findall('game/[@home_name_abbrev="{}"]'.format(team)) + root.findall('game/[@away_name_abbrev="{}"]'.format(team))):
        gdate = g.get('time_date') + ' ' + g.get('ampm') + ' (' + g.get('time_zone') + ')' 
        game = Game(g.get('game_data_directory'), g.get('status'), g.get('inning'), g.get('home_name_abbrev'), g.get('away_name_abbrev'), gdate)
        games.append(game)
    return games

### MAIN ###      
if __name__ == "__main__": 
    t = main(sys.argv[1:])
    games = get_game(t)

# Create new crontab temp file, open to write
    # shutil.copy ("cron_template.txt", "crontab.tmp")
    # CRONTMP  = open("crontab.tmp", "a")

# SETUP crontab
    cron = CronTab(user=True)    
    print '%d %s game(s) today.'  %(len(games), t)  
    for game in games: 
        print '\t%s vs %s at %s (%s).'  %(game.home, game.away, game.date, game.status)
# IF STATUS = IN PROGRESS, THEN FORK MONITOR, 
# ELSE IF STATUS <> IN PROGRESS, APPEND GAME TO NEW CRONTAB FILE
        if (game.status == "In Progress"): 
            print "Monitor game that is in progress!"
        else:
            gamehour = int(game.date[11:12])
            if (game.date[16:18] == "PM"):
                gamehour = gamehour + 12
            gamemin = int(game.date[13:15])
            print "Schedule game monitor for ", gamehour, "#",gamemin,"# from #", game.date,"#", game.date[16:18]
            job = cron.new(command='~/Dev/MLBELL/mlbell_monitor.py -tPHI')
            job.minute.on(gamemin)
            job.hour.on(gamehour)
            job.enable

#            CRONTMP.write("{0} {1} * * *  ~/Dev/MLBELL/mlbell_monitor.py -tPHI\n".format(gamemin, gamehour))
#    CRONTMP.close()
cron.write( 'crontabtmp.txt' )
#!/usr/bin/python
# mlb_monitor.py - application to monitor a current game.

import sys, getopt, time, datetime
import pigpio
from bell import bell
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
   team = 'PHI'
   datestr=datetime.date.today().strftime('%Y-%m-%d')
   monitor = 'HR'
   try:
      opts, args = getopt.getopt(sys.argv[1:],"ht:g:d:m:",["team=","gamepath=","date=","monitor="])
   except getopt.GetoptError:
      print 'mlbell_monitor.py -t <team> -d <YYYY-MM-DD> -m <S/R/HR>'
      sys.exit(2)
   for opt, arg in opts:
      if opt in ('-h','--help'):
         print 'mlbell_monitor.py -t <team> -d <YYYY-MM-DD> -m <S/R/HR>'
         sys.exit()
      elif opt in ("-t", "--team"):
         team = arg.upper()
      elif opt in ("-m", "--monitor"):
          if arg.upper() in ("S", "R", "HR"):
              monitor = arg.upper()
      elif opt in ("-d", "--date"):
          datestr = arg
          # Validate date string?
          #REGEX for date format YYYY-MM-DD: ^(20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$
          # if re.match("^(20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$", datestr): ....

   return team, datestr, monitor

def parse_game(url, team): #Parse miniscoreboard.xml
    try:
        req = requests.get(url, timeout=20)
    except requests.exceptions.RequestException as e:
        print 'parse_game request error: ', e
    else:
        root = ET.fromstring(req.text)

    #### LOCAL FILE TEST ####
    # ms = ET.parse(open("miniscoreboard.xml", "r"))
    
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

def update_game(g): #update game in progress
    try:
        req = requests.get(g.gameuri, timeout=20)
    except requests.exceptions.RequestException as e:  
        print 'update_game requests error', e
        sys.exit(1)
    else:
        root = ET.fromstring(req.text)
        
    runs = root.find('linescore/r')
    homeruns = root.find('linescore/hr')
    g.status = root.find('game_status[@status]').get('status')
    g.inning = root.find('game_status[@inning]').get('inning')
    g.lastupdate = time.strftime("%H:%M:%S")
    g.homeR = runs.get('home')
    g.homeHR = homeruns.get('home')
    g.awayR = runs.get('away')
    g.awayHR = homeruns.get('away')
    return(g)

def get_game(team, datestr = time.strftime("year_%Y/month_%m/day_%d/") ):
# Build a list of all games that "team" is playing "datestr" (or today, if datestr not passed in)
    url = "http://gd2.mlb.com/components/game/mlb/" + datestr + "epg.xml"
    games = []
    try:
        req = requests.get(url, timeout=20)
    except requests.exceptions.RequestException as e:
        print 'get_game request error: ', e
    else:
        root = ET.fromstring(req.text)
        
    #### LOCAL FILE TEST ####
    #epg = /.parse(open("epg2.xml", "r"))
    #### END LOCAL FILE TEST ####
    
    #Now, parse epg.xml, looking for any games with "Team"
    for g in (root.findall('game/[@home_name_abbrev="{}"]'.format(team)) + \
            root.findall('game/[@away_name_abbrev="{}"]'.format(team))):
        gdate = g.get('time_date') + ' ' + g.get('ampm') + \
            ' (' + g.get('time_zone') + ')' 
        game = Game(g.get('game_data_directory'), g.get('status'), \
            g.get('inning'), g.get('home_name_abbrev'), \
            g.get('away_name_abbrev'), gdate)
        games.append(game)
    return games

### MAIN ###      
if __name__ == "__main__": 
    t,d,m = main(sys.argv[1:])
    games = get_game(t)
    print '%d %s game(s) today.'  %(len(games), t)  
    for game in games: 
        print '\t%s vs %s at %s (%s).'  \
            %(game.home, game.away, game.date, game.status)
    for game in games: 
        if (game.status in ["In Progress","Warmup","Pre-Game"]):
            url = "http://gd2.mlb.com" + game.gameuri + "/miniscoreboard.xml"
            g = parse_game(url,t)
            print "Time [INNING]\t%s R (HR)\t%s R (HR)"%(g.home, g.away)
            print "%s [%s]\t    %s (%s)\t    %s (%s)"\
                %(g.lastupdate, g.inning, g.homeR, g.homeHR, g.awayR, g.awayHR)
            sys.stdout.flush()
            score = [g.homeR, g.homeHR, g.awayR, g.awayHR]
            while (g.status in ["In Progress","Warmup","Pre-Game"]):
                g = update_game(g)
                if not(score == [g.homeR, g.homeHR, g.awayR, g.awayHR]):
                    # Okay, the score has changed, so print it...
                    print "%s [%s]\t    %s (%s)\t    %s (%s)"\
                            %(g.lastupdate, g.inning, g.homeR, \
                            g.homeHR, g.awayR, g.awayHR)
                    sys.stdout.flush()
                    # If monitor (m) is S, then ring bell...
                    # Else if m is HR, then check if team hit homerun,
                    # Else if m is R, then check if team scored a run...
                    if (m == "S"):
                        bell()
                    elif (m == "HR"):
                        if (((g.home == t) and not(g.homeHR == score[1])) \
                            or ((g.away == t) and not(g.awayHR == score[3]))):
                            bell()
                    elif (m == "R"):
                        if (((g.home == t) and not(g.homeR == score[0])) \
                            or ((g.away == t) and not(g.awayR == score[2]))):
                            bell()
                # Save old score, for comparision...
            	score = [g.homeR, g.homeHR, g.awayR, g.awayHR]
                time.sleep(15)
            #Should be end of game... or maybe delay?
            print "Status: %s" % (g.status)

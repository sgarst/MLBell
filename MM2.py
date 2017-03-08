#!/usr/bin/python
# mlb_monitor.py - application to monitor a current game.

import sys, getopt, time
#import pigpio
#from bell import bell
#from urllib2 import Request, urlopen, URLError
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
      opts, args = getopt.getopt(argv,"ht:g:d:",["team=","gamepath=","date="])
   except getopt.GetoptError:
      print 'mlbell.py -t <team> -g <gamepath> -d <date>'
      sys.exit(2)
   for opt, arg in opts:
      if opt in ('-h','--help'):
         print 'mlbell_monitor.py -t <team> -g <gamepath> -d <date>'
         sys.exit()
      elif opt in ("-t", "--team"):
         team = arg.upper()
      elif opt in ("-g", "--gamepath"):
         gameuri = "http://gd2.mlb.com/components/game/mlb/" + arg   
      elif opt in ("-d", "--date"):
          datestr = datetime.date.today().strftime('%Y-%m-%d')
   return team, gameuri

def parse_game(url, team): #Parse miniscoreboard.xml
    try:
        req = requests.get(url, timeout=10)
    except req.RequestException as e:
        print 'parse_game request error: ', e
    else:
#        print 'parge_game request success: ', req.status_code
        root = ET.fromstring(req.text)

    #### LOCAL FILE TEST ####
    # ms = ET.parse(open("miniscoreboard.xml", "r"))
    
#    root = ms.getroot()
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
        req = requests.get(g.gameuri, timeout=10)
    except req.RequestException as e:
            print 'update_game request error: ', e
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
        req = requests.get(url, timeout=10)
    except req.RequestException as e:
        print 'get_game request error: ', e
    else:
        root = ET.fromstring(req.text)
        
    #### LOCAL FILE TEST ####
    #epg = /.parse(open("epg2.xml", "r"))
    #### END LOCAL FILE TEST ####
    
    #Now, parse epg.xml, looking for any games with "Team"
    for g in (root.findall('game/[@home_name_abbrev="{}"]'.format(team)) + root.findall('game/[@away_name_abbrev="{}"]'.format(team))):
        gdate = g.get('time_date') + ' ' + g.get('ampm') + ' (' + g.get('time_zone') + ')' 
        game = Game(g.get('game_data_directory'), g.get('status'), g.get('inning'), g.get('home_name_abbrev'), g.get('away_name_abbrev'), gdate)
        games.append(game)
    return games

### MAIN ###      
if __name__ == "__main__": 
    t,g = main(sys.argv[1:])
    games = get_game(t)
    print '%d %s game(s) today.'  %(len(games), t)  
    for game in games: 
        print '\t%s vs %s at %s (%s).'  %(game.home, game.away, game.date, game.status)
    for game in games: 
        if (game.status in ["In Progress","Warming Up"]):
            url = "http://gd2.mlb.com" + game.gameuri + "/miniscoreboard.xml"
            g = parse_game(url,t)
            print "Time [INNING]\t%s R (HR)\t%s R (HR)"%(g.home, g.away)
            print "%s [%s]\t    %s (%s)\t    %s (%s)"%(g.lastupdate, g.inning, g.homeR, g.homeHR, g.awayR, g.awayHR)
            while (g.status in ["In Progress","Warming Up"]):
                score = [g.homeR, g.homeHR, g.awayR, g.awayHR]
                g = update_game(g)
                if not(score == [g.homeR, g.homeHR, g.awayR, g.awayHR]):
                    # IF A HOMERUN, RING BELL!!!
                    if ((not(g.homeHR == score[1]) and (t == g.home)) or (not(g.awayHR == score[3]) and (t == g.away))):
#                        bell()
			print "\nBELL BELL BELL\n"
            	score = [g.homeR, g.homeHR, g.awayR, g.awayHR]
                time.sleep(30)
            print "Status: %s" % (g.status)

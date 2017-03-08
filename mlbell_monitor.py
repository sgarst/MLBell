#!/usr/bin/python
# mlb_monitor.py - application to monitor a current game.

import sys, getopt, time, pigpio
from bell import bell
from urllib2 import Request, urlopen, URLError
import xml.etree.cElementTree as ET

class Game:
    def __init__(self, gameuri, status, home, away, date):
        self.gameuri = gameuri
        self.status = status
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
    req = Request(url)
    try:
        response = urlopen(req)
    except URLError as e:
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
    else:
        ms = ET.parse(response)

    #### LOCAL FILE TEST ####
    # ms = ET.parse(open("miniscoreboard.xml", "r"))
    
    root = ms.getroot()
    status = root.find('game_status[@status]').get('status')
    date = root.get('id')[0:9]
    runs = root.find('linescore/r')
    homeruns = root.find('linescore/hr')
    
    # Create game object, return
    g = Game(url, status, root.get('home_name_abbrev'), root.get('away_name_abbrev'), date)
    g.lastupdate = time.strftime("%H:%M:%S")
    g.homeR = runs.get('home')
    g.awayR = runs.get('away')
    g.homeHR = homeruns.get('home')
    g.awayHR = homeruns.get('away')
    return(g)

def update_game(g): #update game in progress
    req = Request(g.gameuri)
    try:
        response = urlopen(req)
    except URLError as e:
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
    else:
        ms = ET.parse(response)

    root = ms.getroot()
    runs = root.find('linescore/r')
    homeruns = root.find('linescore/hr')
    g.status = root.find('game_status[@status]').get('status')
    g.lastupdate = time.strftime("%H:%M:%S")
    g.homeR = runs.get('home')
    g.homeHR = homeruns.get('home')
    g.awayR = runs.get('away')
    g.awayHR = homeruns.get('away')
    return(g)

def get_game(team, datestr = time.strftime("year_%Y/month_%m/day_%d/") ):
# Build a list of all games that "team" is playing "datestr" (or today, if datestr not passed in)
    url = "http://gd2.mlb.com/components/game/mlb/" + datestr + "epg.xml"
    req = Request(url)
    games = []
    try:
        response = urlopen(req)
    except URLError as e:
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
    else:
        epg = ET.parse(response)

    #### LOCAL FILE TEST ####
    #epg = ET.parse(open("epg2.xml", "r"))
    #### END LOCAL FILE TEST ####
    
    #Now, parse epg.xml, looking for any games with "Team"
    root = epg.getroot()
    for g in (root.findall('game/[@home_name_abbrev="{}"]'.format(team)) + root.findall('game/[@away_name_abbrev="{}"]'.format(team))):
        gdate = g.get('time_date') + ' ' + g.get('ampm') + ' (' + g.get('time_zone') + ')' 
        game = Game(g.get('game_data_directory'), g.get('status'), g.get('home_name_abbrev'), g.get('away_name_abbrev'), gdate)
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
        if (game.status in ["In Progress", "Warming Up"]):
            url = "http://gd2.mlb.com" + game.gameuri + "/miniscoreboard.xml"
            g = parse_game(url,t)
            print "Time\t\t%s R (HR)\t%s R (HR)"%(g.home, g.away)
            print "%s\t    %s (%s)\t    %s (%s)"%(g.lastupdate, g.homeR, g.homeHR, g.awayR, g.awayHR)
            while (g.status == "In Progress"):
                score = [g.homeR, g.homeHR, g.awayR, g.awayHR]
                g = update_game(g)
                if not(score == [g.homeR, g.homeHR, g.awayR, g.awayHR]):
                    print "%s\t    %s (%s)\t    %s (%s)"%(g.lastupdate, g.homeR, g.homeHR, g.awayR, g.awayHR)
                    # IF A HOMERUN, RING BELL!!!
                    if ((not(g.homeHR == score.homeHR) and (t == g.home)) or (not(g.awayHR == score.awayHR) and (t == g.away))):
                        bell()
                    score = [g.homeR, g.homeHR, g.awayR, g.awayHR]
                time.sleep(30)
            print "Status: %s" % (g.status)

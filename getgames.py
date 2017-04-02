#!/usr/bin/python
# getgames.py - Print all games out for date...

import sys, getopt, time, datetime, re
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
   team = 'ALL'
   gamedate=datetime.date.today()
   try:
      opts, args = getopt.getopt(argv,"ht:d:",["team=", "date="])
   except getopt.GetoptError:
      print 'getgames.py -t <team or ALL>  -d <date YYYY-MM-DD>'
      sys.exit(2)
   for opt, arg in opts:
      if opt in ('-h','--help'):
         print 'getgames.py -t <team or ALL>  -d <date YYYY-MM-DD>'
         sys.exit()
      elif opt in ("-t", "--team"):
          #Not validating teams...
         team = arg.upper()
      elif opt in ("-d", "--date"):
          #validating format... but not dates (like April 31st)
          if re.match("^(20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$", arg):
              gamedate=datetime.datetime.strptime(arg,'%Y-%m-%d')
   
   return team, gamedate

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
    #If team = ALL, then dump all games into game array, else
    #only add games by team t
    if t == 'ALL':
        for g in root:
            dt = g.get('time_date') + " " + g.get('ampm')
            gamedate = datetime.datetime.strptime(dt, '%Y/%m/%d %I:%M %p')
            game = Game(g.get('game_data_directory'), g.get('status'), g.get('inning'), \
                g.get('home_name_abbrev'), g.get('away_name_abbrev'), gamedate)
            games.append(game)
    else:
        for g in (root.findall('game/[@home_name_abbrev="{}"]'.format(team)) \
            + root.findall('game/[@away_name_abbrev="{}"]'.format(team))):
            dt = g.get('time_date') + " " + g.get('ampm')
            gamedate = datetime.datetime.strptime(dt, '%Y/%m/%d %I:%M %p')
            game = Game(g.get('game_data_directory'), g.get('status'), g.get('inning'), \
                g.get('home_name_abbrev'), g.get('away_name_abbrev'), gamedate)
            games.append(game)
    return games

### MAIN ###
if __name__ == "__main__":
    t,d = main(sys.argv[1:])
    games = get_game(t,d)
    if not (games):
        print 'No games for %s on %s.' %(t, d.strftime('%m/%d/%Y'))
        sys.exit()
    print '%i game(s) on %s:' %(len(games), d.strftime('%m/%d/%Y'))
    for game in games:
        print '%s vs %s at %s (%s)' \
             %(game.home, game.away, game.date.strftime('%I:%M %p'), game.status )

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
   gameuri = ''
   monitor = 'HR'
   try:
      opts, args = getopt.getopt(sys.argv[1:],"ht:g:d:m:",["team=","gamepath=","date=","monitor="])
   except getopt.GetoptError:
      print 'mlbell_monitor.py -t <team> -g <gamepath> -d <YYYY-MM-DD> -m <S/R/HR>'
      sys.exit(2)
   for opt, arg in opts:
      if opt in ('-h','--help'):
         print 'mlbell_monitor.py -t <team> -g <gamepath> -d <YYYY-MM-DD> -m <S/R/HR>'
         sys.exit()
      elif opt in ("-t", "--team"):
         team = arg.upper()
      elif opt in ("-g", "--gamepath"):
         gameuri = "http://gd2.mlb.com/components/game/mlb/" + arg   
      elif opt in ("-m", "--monitor"):
          if arg.upper() in ("S", "R", "HR"):
              monitor = arg.upper()
      elif opt in ("-d", "--date"):
          datestr = arg
          # Validate date string?
          #REGEX for date format YYYY-MM-DD: ^(20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$
          # if re.match("^(20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$", datestr): ....
          
   return team, datestr, gameuri, monitor


### MAIN ###      
if __name__ == "__main__": 
    t,d,g,m = main(sys.argv[1:])
    print sys.argv
    print '\nTeam: %s, Date: %s, Monitor: %s' %(t, d, m)

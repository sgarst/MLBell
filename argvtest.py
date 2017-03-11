#!/usr/bin/python
# mlbell_schedule.py - determine if there are any games today, and if so set up monitoring.

import sys, getopt, time, datetime

def main(argv):
   team = 'PHI'
   datestr=datetime.date.today().strftime('%Y-%m-%d')
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
          datestr = arg
          # REGEX for date format YYYY-MM-DD: ^(20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$
          # if re.match("^(20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$", datestr):
   print "Args: T", team, ", Date: ", datestr
   return team, datestr

### MAIN ###      
if __name__ == "__main__": 
    t,d = main(sys.argv[1:])
    print "Returned team: ", t, ", Date: ", d
    # recast 2017-03-16 to year_2017/month_03/day_16/
    datestr = 'year_{}/month_{}/day_{}/'.format(d[0:4], d[5:7],d[8:10])
    print datestr
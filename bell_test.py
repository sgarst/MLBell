#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, argparse, time, datetime, json, pigpio
from urllib2 import Request, urlopen, URLError
import xml.etree.cElementTree as ET
from bell import bell

def main():
  print "Ringing bell...."
  bell()
  print "Done."

if __name__ == "__main__":
    main();

#! /usr/bin/python
"""Ouput ephemeris information that might be interesting

Parts taken from: http://www.jnrowe.ukfsn.org/data/mcnaught_ephemeris.txt
"""

__license__ = "Public Domain"

import ephem
import math
import urllib2

# http://celestrak.com/NORAD/elements/stations.txt
def GrabStations():
  url = 'http://celestrak.com/NORAD/elements/visual.txt'
  stations = []
  row = 0
  for line in urllib2.urlopen(url).read().split('\n'):
    line = line.rstrip()
    if row == 0:
      station = line
    elif row == 1:
      line1 = line
    elif row == 2:
      stations.append(ephem.readtle(station, line1, line))
      row = -1
    else:
      raise "Wrong number", row
    row += 1
  return stations

# Comets
# http://cfa-www.harvard.edu/iau/Ephemerides/Comets/Soft03Cmt.txt
comet = ephem.readdb('17P/Holmes,e,19.1126,326.8646,24.2712,3.618414,0.1431946,0.43256415,25.1267,10/27.0/2007,2000,g 10.0,6.0')

sun = ephem.Sun()
mars = ephem.Mars()
jupiter = ephem.Jupiter()

home = ephem.Observer()
home.lat = '-19.95298752640343'
home.long = '-43.93315000567806'
home.elev = 802
home.date = ephem.now()

def get_time(t):
  try:
      ret = str(ephem.localtime(t)) # .split(" ")[1][0:8]
  except ValueError:
      ret = '-'

  return ret

def get_transit_info(object, move_date = False):
  global home

  object.compute(home)
  save_date = home.date
  try:
    obj_transit = home.next_transit(object)
    obj_rise = home.next_rising(object)
    obj_set =  home.next_setting(object)
    duration = 0
    if obj_rise and obj_set:
      duration = (obj_set- obj_rise) / ephem.minute
  except ephem.NeverUpError:
    obj_rise, obj_transit, obj_set, duration = (None, None, None, None)

  if not move_date:
    home.date = save_date

  return obj_rise, obj_transit, obj_set, duration
  
def get_transit_satellite(object):
  global home

  object.compute(home)
  save_date = home.date
  myhorizon = 40
  ret = {}
  try:
    ret['transit'] = home.next_transit(object)
    ret['rise'] = ret['transit']
    ret['set'] = ret['transit']
    ret['alt'] = object.alt
    if object.eclipsed or object.alt <= math.radians(myhorizon) or object.alt >= math.radians(180 - myhorizon):
      ret = {}
    else:
      print "%s up with alt %s mag %f" % (object.name, str(object.alt), object.mag)
      ret['mag'] = object.mag
      ret['eclipsed'] = object.eclipsed
    duration = 0
  except ephem.NeverUpError:
    ret = {}

  home.date = save_date

  return ret
 
def print_info(object, info): 
  rise, transit, set, duration = info
  if not rise:
    print "  %s never rises" % object.name
  else:
    print "  %s rises   @%s" % (object.name, get_time(rise))
    print "  %s transit @%s" % (object.name, get_time(transit))
    print "  %s sets    @%s" % (object.name, get_time(set))
    print "  Duration %0d minutes" % duration

def GetNext(obj, days=2):
  ret = []
  save_date = home.date
  while (home.date - save_date) < days:
    info = get_transit_info(obj, move_date=True)
    if info[0]:
      rise, transit, set, duration = info
      thedate = str(ephem.localtime(transit)).split(' ')[0]
      ret.append((thedate, get_time(rise),    'rise', obj.name))
      ret.append((thedate, get_time(transit), 'transit', obj.name))
      ret.append((thedate, get_time(set),     'set', obj.name))
    else:
      home.date += 1
  home.date = save_date
  return ret

def GetNextSatellite(obj):
  ret = []
  save_date = home.date
  try:
    thedate = str(ephem.localtime(home.date)).split(' ')[0]
  except ValueError:
    thedate = str(home.date).split(' ')[0]
  info = get_transit_satellite(obj)
  if 'transit' in info:
    transit = info['transit']
    ret.append((thedate, get_time(transit), 'transit', '%s %s %s' % (obj.name, info['mag'], info['eclipsed'])))
  home.date = save_date
  return ret

def DropDaylight(lst):
  ret = []
  prev_date = None
  for thedate, thetime, rts, name in lst:
    if prev_date != thedate:
      isDaylight = False
      prev_date = thedate
    if name == 'Sun' and rts == 'rise':
      isDaylight = True
    elif name == 'Sun' and rts == 'set':
      isDaylight = False
    if not isDaylight or name == 'Sun':
      ret.append((thedate, thetime, rts, name))
  return ret


def PrintList(lst):
  prev_date = None
  for thedate, thetime, rts, name in lst:
    if name == 'Sun' and rts == 'transit':
      continue
    if prev_date != thedate:
      print "%s" % thedate
      prev_date = thedate
    print "  %-20s %-7s @%s" % (name, rts, thetime) 

if __name__ == "__main__":
  stations = GrabStations()
  home.date = ephem.now() - 1
  lst = []
  lst += GetNext(sun)
  for station in stations:
    lst += GetNextSatellite(station)
  lst += GetNext(comet)
  lst += GetNext(mars)
  lst += GetNext(jupiter)
  lst.sort()
  lst = DropDaylight(lst)
  PrintList(lst)

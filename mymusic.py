#!/usr/bin/python
#

"""Create a directory of links from a m3u file.

"""

__author__ = 'scott@forusers.com (scottkirkwood)'

import os

def main(argv):
  fname = '/home/scott/mymusic/PartyMusic.m3u'
  todir = '/home/scott/links'

  rootpath = os.path.split(fname)[0]
  for line in open(fname):
    if line[0] == '#':
      continue
    from_name = line.rstrip()
    if not os.path.exists(from_name):
      from_name = os.path.join(rootpath, from_name)

    if os.path.exists(from_name):
      to_name = os.path.basename(from_name)
      to_name = os.path.join(todir, to_name)
      print 'ln -s %s %s' % (from_name, to_name)
      try:
        os.link(from_name, to_name)
      except OSError, e:
        print e, to_name


if __name__ == '__main__':
  main(None)

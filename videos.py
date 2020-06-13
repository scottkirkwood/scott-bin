#!/usr/bin/python
# -*- encoding: latin1 -*-
#
# Copyright 2006 Google Inc. All Rights Reserved.

""" 
List the videos available
"""
__author__ = 'scottkirkwood@google.com (Scott Kirkwood)'

import os
import optparse
import re
import subprocess
import memoize

def list_videos(use_cache, directory = '/auto/videos/Eng', ext='.avi'):
  if use_cache:
    time_out = 24 * 60 * 60 # 24 hours
  else:
    time_out = 0
  SEP = '|'
  mem = memoize.Memoize(time_out)
  keyname = 'videos'
  results = mem.Retrieve(keyname)
  if results != None:
    tmp_results = [x.split(SEP) for x in results.split('\n')]
    results = []
    for result in tmp_results:
      if len(result) == 3:
        results.append((int(result[0]), result[1], int(result[2])))
    return results
    

  results = []
  for root, dirs, files in os.walk(directory):
    for name in files:
      full_name = os.path.join(root, name)
      if name.endswith(ext):
        stats = os.stat(full_name)
        results.append((stats.st_mtime, full_name, stats.st_size))
  
  results.sort()
  
  toStore = []
  for result in results:
    toStore.append(SEP.join([str(x) for x in result]))
  
  mem.Store(keyname, '\n'.join(toStore))
  return results

def find_video(videos, regex):
  """ Copies the first video that matches the regex, first being the most recent """
  re_seek = re.compile(regex, re.IGNORECASE)
  for video_info in videos[::-1]:
    if re_seek.search(video_info[1]):
      return video_info[1]
  return ''
  
def rsync_video(fname, dest):
  """ Copy file from a to b """
  print "Will copy '%s' to '%s'" % (fname, dest)
  args=['rsync', '--progress', '--copy-links', fname, dest]
  subprocess.call(args)

if __name__ == '__main__':
  LIMIT = -1
  DESTDIR = "/usr/local/google/home/videos/"
  
  parser = optparse.OptionParser()
  parser.add_option('-k', '--kill', dest='no_cache', action='store_true',
    help="Kill Cache")
  parser.add_option('-n', '--limit', dest='limit',
    help="Only show the last N")
  parser.add_option('--cp', dest='copy_file', metavar="FILENAME",
    help="Copy first file that matches this regex locally to %s" % DESTDIR)
  (options, args) = parser.parse_args()

  videos = list_videos(not options.no_cache)
  
  if options.copy_file:
    video_name = find_video(videos, options.copy_file)
    rsync_video(video_name, DESTDIR)
  elif options.limit:
    for video_info in videos[-int(options.limi):]:
      print video_info[1]
  else:
    for video_info in videos:
      print video_info[1]

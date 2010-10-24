#!/usr/bin/python
#
# Copyright 2010 Scott Kirkwood All Rights Reserved.

"""Delete the torrents files that weren't completed.

If you don't want to wait for the torrent to finish and you don't want to have
incomplete torrent files, this will save you.
"""

__author__ = 'scott@forusers.com (Scott Kirkwood)'

import hashlib
import os
import sys

try:
  from BitTorrent.bencode import bdecode
except:
  print 'You need to run "sudo apt-get python-bittorrent" or equivalent'
  sys.exit(-1)


def ReadTorrent(fname):
  fo = open(fname)
  torrent = bdecode(fo.read())
  fo.close
  return torrent


def Sha1(fname):
  fo = open(fname)
  signature = hashlib.sha1()
  signature.update(fo.read())
  fo.close()
  return signature.digest()


def SaveFile(to_delete):
  print '%d files to delete' % len(to_delete)
  fname = 'todelete.txt'
  fo = open(fname, 'w')
  for f in to_delete:
    fo.write('%s\n' % f)
  fo.close()
  print 'The files were saved to %s' % fname
  print 'Run:'
  print 'xargs -a %s -d \'\\\\n\' rm' % fname
  print 'To delete them after looking at the file'


def CheckFiles(torrent_info, folder):
  lstfiles = dict([(x, True) for x in os.listdir(folder)])
  files = torrent_info['info']['files']
  to_delete = []
  for file in files:
    path = os.path.join(*file['path'])
    if path not in lstfiles:
      print 'Missing file', path

    fullpath = os.path.join(folder, path)
    signature = Sha1(fullpath)
    sha1 = file['sha1']
    if sha1 != signature:
      print 'Signature doesn\'t match for %s' % path
      to_delete.append(fullpath)
    else:
      print 'Ok %s' % path
  SaveFile(to_delete)


def Main():
  import optparse
  usage = 'Usage: %prog torrent-file download-dir'
  parser = optparse.OptionParser(usage)
  options, argv = parser.parse_args()
  
  if len(argv) != 2:
    parser.error('Two parameters required')
    sys.exit(-2)


  torrent_info = ReadTorrent(argv[0])
  CheckFiles(torrent_info, argv[1])


if __name__ == '__main__':
  Main()

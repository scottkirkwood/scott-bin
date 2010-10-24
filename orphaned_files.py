#!/usr/bin/python

"""Deletes the subtitles if the matching video is gone.

This is used as a cronjob so that I can delete the .avi, etc files and the
.sub or srt files get deleted automatically (eventually).
"""

import os
from glob import glob
import optparse


def GlobToDelete(dir, to_dels):
  ret = []
  for to_del in to_dels:
    for fname in glob(os.path.join(dir, to_del)):
      ret.append(fname)
  return ret


def ToDelete(all_files, to_dels):
  to_del_dict = dict((x, True) for x in to_dels)
  all_base_dict = {}
  ret = []
  for file in all_files:
    if file in to_del_dict:
      continue
    all_base_dict.update({os.path.splitext(file)[0]: True})

  for to_del in to_dels:
    base_to_del = os.path.splitext(to_del)[0]
    if base_to_del in all_base_dict:
      continue
    ret.append(to_del)
  return ret


def Delete(to_dels, verbose, do_it):
  for to_del in to_dels:
    if verbose:
      print 'Delete', to_del
    if do_it:
      os.unlink(to_del)


if __name__ == '__main__':
  parser = optparse.OptionParser()
  parser.add_option('-d', '--dir', dest='dir', 
                    default='/home/scott/videos',
                    help='Folder to examine')
  parser.add_option('--to_delete', dest='to_delete',
                    default='*.srt|*.sub|*.txt',
                    help='Files to examine and delete ex. "*.srt|*.sub"')
  parser.add_option('--dry_run', dest='dry_run', action='store_true',
                    help='Don\'t do it.')
  parser.add_option('-q', dest='quiet', action='store_true',
                    help='Be quiet.')
  options, args = parser.parse_args()
  all_files = GlobToDelete(options.dir, ['*'])
  maybe_to_dels = GlobToDelete(options.dir, options.to_delete.split('|'))
  to_dels = ToDelete(all_files, maybe_to_dels)
  Delete(to_dels, not options.quiet, not options.dry_run)

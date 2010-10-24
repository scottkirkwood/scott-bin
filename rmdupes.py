#!/usr/bin/python
"""This little program uses a three step process to find and remove duplicates.

First you run calc_dupes which creates '/tmp/dupes.txt'
The you run rm_dupes_sh which creates '/tmp/rm_dupes.sh'
Then you run the rm_dupes.sh after verfying it's correct.
"""

import os
import subprocess
import optparse

def calc_dupes(outfile, dirs):
  """Create a dupes file by running fdupes.
  Args:
    outfile: name of file to create.
    dirs: list of directories to find duplicates.
  """
  args = ['fdupes',
          '--recurse', '--noempty', '--omitfirst'] + dirs
  args_str = ' '.join(args)
  print 'Running: %r' % args_str
  proc = subprocess.Popen(args, stdout=subprocess.PIPE)
  stdout = proc.communicate()[0]
  if proc.return_code:
    print 'Error calling fdupes %s' % args_str
    sys.exit(ret)
  outf = open(outfile, 'w')
  outf.write(stdout)
  outf.close()
  print 'Wrote file %r' % outfile


def rm_dupes_sh(dupes_file, outfile, dirs):
  outf = open(outfile, "w")
  for line in open(dupes_file):
    line = line.rstrip()
    if line:
      outf.write('rm \'%s\'\n' % line)
  outf.close()

if __name__ == '__main__':
  parser = optparse.OptionParser('%prog dir1 dir2 ... where you want to keep files in dir1')
  dupes_file = '/tmp/dupes.txt'
  rm_dupes_file = '/tmp/rm_dupes.sh'
  options, argv = parser.parse_args()
  if len(argv) == 0:
    print 'Need one or more dirs to scan, first one is a keeper'
    sys.exit(-1)
  calc_dupes(dupes_file, argv)
  print 'Creating %r' % rm_dupes_file
  rm_dupes_sh(dupes_file, rm_dupes_file)

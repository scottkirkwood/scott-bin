#! /usr/bin/env python

import subprocess
import sys
import optparse

def BackupFiles(backup_list, dest_dir):
  cmd = ['rdiff-backup',
      '--include-globbing-filelist', backup_list,
      '/',
      dest_dir]
  ret = subprocess.call(cmd)

  if ret == 0:
      print "Success"
  else:
      print "Error:", ret
      sys.exit(-1)

def RemoveOld(dest_dir):
  cmd = ['rdiff-backup',
      '--remove-older-than', '1M',
      dest_dir,
      ]
  ret = subprocess.call(cmd)

def ListSelections(outfile):
  cmd = ['dpkg',
      '--get-selections']
  output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
  fo = open(outfile, 'w')
  fo.write(output)
  fo.close()

def ListCronJobs(outfile):
  cmd = ['crontab', '-l']
  output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
  fo = open(outfile, 'w')
  fo.write(output)
  fo.close()

if __name__ == '__main__':
  parser = optparse.OptionParser()
  parser.add_option('--notify', dest='notify', action='store_true',
                    help='Show the notify')
  options, argv = parser.parse_args()
  if options.notify:
    import pynotify
    pynotify.init('Backup')
    notification = pynotify.Notification('Backup', 'Started the backup')
    notification.show()
  ListSelections('/home/scott/bin/apt-selections.txt')
  ListCronJobs('/home/scott/bin/cron-jobs.txt')
  backup_list = '/home/scott/bin/backup-list.txt'
  dest_dir = 'scott@pluto::/backup/scott/'
  BackupFiles(backup_list, dest_dir)
  RemoveOld(dest_dir)
  if options.notify:
    notification = pynotify.Notification('Backup', 'Finished the backup')
    notification.show()

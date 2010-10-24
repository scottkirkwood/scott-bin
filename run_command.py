#!/usr/bin/python2.4
#
# Copyright 2007 Google Inc. All Rights Reserved.

"""Routine to run any command line program.

"""

__author__ = 'scottkirkwood@google.com (Scott Kirkwood)'

import subprocess


class ProgramReturnedErrorException(Exception):
  """Exception Class."""
  def __init__(self, command, errorcode):
    self.command = command
    self.errorcode = errorcode

  def __str__(self):
    return '"%s" failed to execute correctly with error %d' % (self.command,

                                                               self.errorcode)
def RunCommand(args, output_command = False, ignore_retcode = False,
               doit=True):
  """Run a command in the shell, capture all output.
  
  Args:
    args: list of arguments
    output_command: show the output.
    ignore_retcode: Don't throw an exception if the retcode is not 0
    doit: Run the command (defaults to True)
  Returns:
    yields lines of output.
  """
  if output_command:
    print ' '.join(args)
  if not doit:
    return
  proc = subprocess.Popen(' '.join(args), stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT, shell=True)
  for line in proc.stdout:
    yield line
  ret = proc.wait()
  if not ignore_retcode and ret != 0:
    raise ProgramReturnedErrorException(' '.join(args), ret)


def RunPrint(args, output_command = False, ignore_retcode = False, doit=True):
  """Run the command and print each line to stdout."""
  import sys
  for line in RunCommand(args, output_command, ignore_retcode, doit):
    sys.stdout.write(line)


if __name__ == '__main__':
  import sys

  args = sys.argv[1:]
  RunPrint(args, output_command = True)

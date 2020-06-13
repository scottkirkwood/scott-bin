#!/usr/bin/python
#
# Copyright 2008 Google Inc. All Rights Reserved.

"""Simple tool to get the reverse DNS lookup

TODO: Needs some cleanup, parameters, etc.
"""

__author__ = 'scottkirkwood@google.com (Scott Kirkwood)'

import socket
import sys


def main(argv):
  print socket.gethostbyaddr(argv[1])


if __name__ == '__main__':
  main(sys.argv)

"""Escape binary as string.
"""
import os
import sys

if __name__ == '__main__':
  s = sys.stdin.read()
  hex = []
  for c in s:
    hex.append('\\x%x' % ord(c))
  print '"%s"' % ''.join(hex)

#!/usr/bin/python
"""Have no idea what this does!
"""
import re

def ReadFile(fname):
    lines = []
    re_hex = re.compile(r'([0-9a-f]{32})')
    re_key = re.compile(r'([a-z0-9]+):')
    for line in open(fname):
        line = line.strip()
        line = re_hex.sub(r"'\1'", line)
        line = re_key.sub(r"'\1':", line)
        row = eval('{' + line + '}')
        lines.append(row)
    return lines

if __name__ == "__main__":
    import optparse

    parser = optparse.OptionParser()
    options, argv = parser.parse_args()

    list = ReadFile(argv[0])
    print list

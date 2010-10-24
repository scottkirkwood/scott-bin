#! /usr/bin/env python

import subprocess
import optparse
import os.path

places = [ 'http://localhost:2599/']

nofollow = [ '.*creativecommons.org.*']

subprocess.call(['linkchecker', 
    places[0],  
    '--quiet', 
#    '--verbose', 
    '--recursion-level=7',
    '--file-output=text',] +
    ['--ignore-url=%s' for url in nofollow],
    )
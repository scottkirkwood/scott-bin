#! /usr/bin/env python

import subprocess
import glob

for file in glob.glob('*.wav'):
	strNew = file.replace('.wav', '.mp3')
	args = ['toolame', '-b', '128', file, strNew]
	subprocess.call(args)

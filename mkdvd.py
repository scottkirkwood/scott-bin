#! /usr/bin/env python

from subprocess import call
import optparse
import os.path

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-f", "--file",
            dest="strFileName", metavar="<file>",
            help="Full pathname")
        
    parser.add_option("-n", "--num",
            dest="nIndex", type="int", metavar="<num>",
            help="Index of the backup")
            
    (options, args) = parser.parse_args()
    if options.nIndex == None or options.strFileName == None:
        parser.error("incorrect number of arguments")
    
    fname = os.path.basename(options.strFileName)
    
    ret = call(['growisofs',
        '-dvd-compat', # causes closed disk as a side effect
        #'-speed=2', # double speed
        '-Z', '/dev/dvd',
        '-R', # Generate SUSP and RR records using Rock Ridge Protocol
        '-J', # Generate Joliet directory records
#        'driveropts=burnfree', # n
        '-V', fname[-32:], # Volume id (up to 32 chars)
        options.strFileName,
    ])
    if ret == 0:
        print "Success"
    else:
        print "Error:", ret

    
#mkisofs -o /tmp/image.iso -r -J -V "archive_$2" T
#cdrecord dev=0,0 speed=8 -data /tmp/image.iso

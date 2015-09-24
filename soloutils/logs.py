"""
Downloads logs.
"""

import soloutils
from datetime import datetime, timedelta
from scp import SCPClient

def main(args):
    print 'connecting to Solo...'
    solo = soloutils.connect_solo(await=True)

    code, stdout, stderr = soloutils.command(solo, 'ls -p /log | grep -v /')
    files = stdout.strip().split()

    scp = SCPClient(solo.get_transport())
    count = 0
    for item in files:
    	print 'file {} of {}...'.format(count, len(files))
    	scp.get('/log/' + item)
    	count += 1

    print 'complete.'

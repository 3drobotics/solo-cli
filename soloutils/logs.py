"""
Downloads logs.
"""

import soloutils
import os
from datetime import datetime, timedelta
from scp import SCPClient

def main(args):

    os.makedirs('./drone')
    os.makedirs('./controller')

    print 'connecting to Solo...'
    solo = soloutils.connect_solo(await=True)
    code, stdout, stderr = soloutils.command(solo, 'ls -p /log | grep -v /')
    files = stdout.strip().split()

    os.chdir('./drone')
    scp = SCPClient(solo.get_transport())
    count = 0
    for item in files:
    	print 'file {} of {}...'.format(count, len(files))
    	scp.get('/log/' + item)
    	count += 1
    os.chdir('..')

    solo.close()

    print 'connecting to Controller...'
    controller = soloutils.connect_controller(await=True)
    code, stdout, stderr = soloutils.command(controller, 'ls -p /log | grep -v /')
    files = stdout.strip().split()

    os.chdir('./controller')
    scp = SCPClient(controller.get_transport())
    count = 0
    for item in files:
        print 'file {} of {}...'.format(count, len(files))
        scp.get('/log/' + item)
        count += 1
    os.chdir('..')

    controller.close()

    print 'logs download complete.'

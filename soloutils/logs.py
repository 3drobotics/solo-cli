"""
Downloads logs.
"""

import soloutils
from datetime import datetime, timedelta

def main(args):
    print 'connecting to Solo...'
    solo = soloutils.connect_solo(await=True)

    code, stdout, stderr = soloutils.command(solo, 'ls -p | grep -v /')
    print(stdout)
    print(stderr)
    print 'done?'

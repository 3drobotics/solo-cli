"""
Reverts to a clean install of a given version.
"""

import sys
import soloutils
from datetime import datetime, timedelta

def main(args):
    if args['both']:
        group = 'Solo and the Controller'
    if args['solo']:
        group = 'Solo'
    if args['controller']:
        group = 'the Controller'

    # prompt for consent
    print 'you are about to revert all local changes made to {}.'.format(group)
    print 'this process is not reversible.'
    y = raw_input('proceed to revert local changes? [y/N] ')
    if not (y.lower() == 'y' or y.lower() == 'yes'):
        sys.exit(1)

    if not args['current']:
        print 'TODO: only solo revert to "current" works yet.'
        sys.exit(1)

    print 'connecting to {}...'.format(group)

    if args['solo'] or args['both']:
        solo = soloutils.connect_solo(await=True)
    if args['controller'] or args['both']:
        controller = soloutils.connect_controller(await=True)

    if args['solo'] or args['both']:
        soloutils.settings_reset(solo, 'solo')
        print('Solo will continue reverting once it reboots.')
    if args['controller'] or args['both']:
        newstyle = soloutils.settings_reset(controller, 'controller')
        print('Controller will continue reverting once it reboots.')

    dt = datetime.today() + timedelta(minutes=4)
    print('please wait up to three minutes longer for the reset to complete (at {}).'.format(dt.strftime('%-I:%M')))

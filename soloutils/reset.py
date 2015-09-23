"""
Clears the user partition.
"""

import soloutils
from datetime import datetime, timedelta

def main(args):
    # TODO: PROMPT FOR CONSENT

    print 'connecting to Controller...'
    client = soloutils.connect_controller(await=True)

    code = soloutils.command_stream(client, 'sololink_config --settings-reset')
    if code != 0:
        code = soloutils.command_stream(client, 'mkdir -p /log/updates && touch /log/updates/RESETSETTINGS && shutdown -r now')
        if args['controller']:
            print('the Controller will reset once it reboots.')
        else:
            print('Solo will reset once it reboots.')
    else:
        print('reset succeeded!')

    dt = datetime.today() + timedelta(minutes=4)
    print('please wait up to three minutes longer for the reset to complete (at {}).'.format(dt.strftime('%-I:%M')))

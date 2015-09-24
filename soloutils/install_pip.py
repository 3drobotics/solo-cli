import paramiko, base64, time, sys, soloutils
from distutils.version import LooseVersion

# This script operates in two stages: creating the script file
# and then executing it, so we are resilient to network dropouts.

SCRIPT = """
echo hi
"""

def main(args):
    print 'NOTE: this process requires simultaneous access to'
    print 'Solo and to the Internet. if you have not yet done so,'
    print 'run `solo wifi` to connect to Solo and to a local'
    print 'wifi connection simultaneously.'
    print ''

    print 'connecting to solo...'
    solo = soloutils.connect_solo(await=True)

    print 'waiting for Internet connectivity...'
    soloutils.await_net()

    code = soloutils.command_stream(solo, SCRIPT)
    solo.close()
    sys.exit(code)

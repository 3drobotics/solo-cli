"""
Gets info on Solo and the Controller.
"""

import json
import soloutils
import sys
import os
from datetime import datetime, timedelta
from os.path import expanduser

def main(args):
    rsa = os.path.join(expanduser('~'), '.ssh/id_rsa.pub')
    dsa = os.path.join(expanduser('~'), '.ssh/id_dsa.pub')
    if not (os.path.isfile(rsa) or os.path.isfile(dsa)):
        print 'no $HOME/.ssh/id_rsa.pub or $HOME/.ssh/id_dsa.pub file found.'
        print 'run ssh-keygen and try again.'
        sys.exit(1)

    if os.path.isfile(rsa):
        key = open(rsa).read()
    else:
        key = open(dsa).read()

    controller = soloutils.connect_controller(await=True)
    solo = soloutils.connect_solo(await=True)

    soloutils.command(solo, 'test -d .ssh || mkdir -m 0700 .ssh ; echo $\'' + key + '\' >> ~/.ssh/authorized_keys')
    soloutils.command(controller, 'test -d .ssh || mkdir -m 0700 .ssh ; echo $\'' + key + '\' >> ~/.ssh/authorized_keys')
    
    print 'provisioned.'

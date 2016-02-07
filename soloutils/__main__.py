"""
Solo command line utilities.

Usage:
  solo info
  solo wifi --name=<n> [--password=<p>]
  solo flash (drone|controller|both) (latest|current|factory|<version>) [--clean]
  solo flash --list
  solo flash pixhawk <filename>
  solo provision
  solo resize
  solo logs (download)
  solo install-pip
  solo install-smart
  solo install-runit
  solo video (acquire|restore)
  solo script run [--force] <scriptname> [--] [<scriptarg>...]
  solo script (pack|push)

Options:
  -h --help        Show this screen.
  --name=<n>       WiFi network name.
  --password=<p>   WiFi password.
  --list           Lists available updates.
"""

import threading, time

from docopt import docopt
args = docopt(__doc__, version='solo-cli 1.1.0')

import base64, time, sys
import soloutils
from subprocess import Popen
import os

if args['flash']:
    soloutils.flash.main(args)
elif args['info']:
	  soloutils.info.main(args)
elif args['provision']:
    soloutils.provision.main(args)
elif args['wifi']:
    soloutils.wifi.main(args)
elif args['logs']:
    soloutils.logs.main(args)
elif args['install-pip']:
    soloutils.install_pip.main(args)
elif args['install-smart']:
    soloutils.install_smart.main(args)
elif args['install-runit']:
    soloutils.install_runit.main(args)
elif args['resize']:
    soloutils.resize.main(args)
elif args['video']:
    soloutils.video.main(args)
elif args['script']:
    if sys.argv[2] == 'pack':
        if sys.platform.startswith("win"):
            print 'ERROR: "solo script pack" does not yet run on Windows.'
            print 'please follow along with its progress on github.'
            sys.exit(1)

        print 'checking Internet connectivity...'
        soloutils.await_net()

        Popen([os.path.join(os.path.dirname(__file__), 'solocode-pack.sh')] + sys.argv[3:], cwd=os.curdir).communicate()
    elif sys.argv[2] == 'push':
        soloutils.script.push_main(args)
    elif sys.argv[2] == 'run':
        if not args['<scriptname>']:
            print 'Usage: solo script run <scriptname> [<scriptarg>...]'
            sys.exit(1)
        soloutils.script.run_main(args)
    else:
        print('Usage: solo script (pack|push|run)')
        sys.exit(1)
else:
    print 'no argument found.'

sys.exit(0)

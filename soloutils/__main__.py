"""
Solo command line utilities.

Usage:
  solo info
  solo wifi --name=<n> [--password=<p>]
  solo flash (drone|controller|all) (latest|current|factory|<version>) [--clean]
  solo flash --list
  solo provision
  solo resize
  solo logs (download)
  solo install-pip
  solo install-smart
  solo install-runit
  solo video (acquire|restore)

Options:
  -h --help        Show this screen.
  --name=<n>       WiFi network name.
  --password=<p>   WiFi password.
  --list           Lists available updates.
"""

import threading, time

from docopt import docopt
args = docopt(__doc__, version='solo-utils 1.0')

import base64, time, sys
import soloutils

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
else:
    print 'no argument found.'

sys.exit(0)

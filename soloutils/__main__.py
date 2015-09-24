"""Solo utilities.

Usage:
  solo info
  solo wifi --name=<n> --password=<p>
  solo update (solo|controller|both) (latest|<version>)
  solo revert (solo|controller|both) (latest|current|factory|<version>)
  solo provision
  solo logs (download)
  solo install-pip
  solo install-smart

Options:
  -h --help        Show this screen.
  --name=<n>       WiFi network name.
  --password=<p>   WiFi password.

"""

import threading, requests, time

from docopt import docopt
args = docopt(__doc__, version='solo-utils 1.0')

import base64, time, sys
import soloutils

if args['update']:
    soloutils.update.main(args)
elif args['revert']:
	  soloutils.revert.main(args)
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
else:
    print 'no argument found.'

sys.exit(0)

"""Solo utilities.

Usage:
  solo tunnel --name=<n> --password=<p>
  solo update (solo|controller) (latest|current|factory|<version>)

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
else:
    soloutils.tunnel.main(args)

sys.exit(0)

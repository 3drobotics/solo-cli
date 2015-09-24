"""
Gets versions of Solo and the Controller.
"""

import json
import soloutils
from datetime import datetime, timedelta

def main(args):
    print 'connecting to Solo and the Controller...'

    controller = soloutils.connect_controller(await=True)
    solo = soloutils.connect_solo(await=True)

    data = {}
    data['solo'] = soloutils.solo_versions(solo)
    data['pixhawk'] = soloutils.pixhawk_versions(solo)
    data['gimbal'] = soloutils.gimbal_versions(solo)
    data['controller'] = soloutils.controller_versions(controller)

    print json.dumps(data, indent=2, sort_keys=True)

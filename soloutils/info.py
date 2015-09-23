"""
Gets info on Solo and the Controller.
"""

import json
import soloutils
from datetime import datetime, timedelta

def main(args):
    print 'connecting to Solo and the Controller...'

    client = soloutils.connect_controller(await=True)
    code, controller_version, stderr = soloutils.command(client, 'cat /VERSION')
    client.close()

    solo = soloutils.connect_solo(await=True)
    code, solo_version, stderr = soloutils.command(solo, 'cat /VERSION')
    code, pixhawk_version, stderr = soloutils.command(solo, 'cat /PIX_VERSION')
    code, gimbal_version, stderr = soloutils.command(solo, 'cat /AXON_VERSION')
    solo.close()

    data = {}
    data['solo_version'], data['solo_ref'] = solo_version.strip().split()
    data['pixhawk_version'], data['pixhawk_version_apm'], data['pixhawk_version_px4firmware'], data['pixhawk_version_px4nuttx'] = pixhawk_version.strip().split()
    data['gimbal_version'], = gimbal_version.strip().split()
    data['controller_version'], data['controller_ref'] = controller_version.strip().split()

    print json.dumps(data, indent=2, sort_keys=True)

"""
Gets info on Solo and the Controller.
"""

import json
import soloutils
from datetime import datetime, timedelta

def controller_versions(controller):
    code, controller_str, stderr = soloutils.command(controller, 'cat /VERSION')
    version, ref = controller_str.strip().split()
    return {
        "version": version,
        "ref": ref,
    }

def solo_versions(solo):
    code, solo_str, stderr = soloutils.command(solo, 'cat /VERSION')
    version, ref = solo_version.strip().split()
    return {
        "version": version,
        "ref": ref,
    }

def gimbal_versions(solo):
    code, gimbal_str, stderr = soloutils.command(solo, 'cat /AXON_VERSION')
    version, = gimbal_version.strip().split()
    return {
        "version": version,
    }

def pixhawk_versions(solo):
    code, pixhawk_str, stderr = soloutils.command(solo, 'cat /PIX_VERSION')
    version, apm_ref, px4firmware_ref, px4nuttx_ref = pixhawk_str.strip().split()
    return {
        "version": version,
        "apm_ref": apm_ref,
        "px4firmware_ref": px4firmware_ref,
        "px4nuttx_ref": px4nuttx_ref,
    }

def main(args):
    print 'connecting to Solo and the Controller...'

    controller = soloutils.connect_controller(await=False)
    solo = soloutils.connect_solo(await=False)

    data = {}
    data['solo'] = solo_versions(solo)
    data['pixhawk'] = solo_versions(solo)
    data['gimbal'] = solo_versions(solo)
    data['controller'] = controller_versions(controller)

    print json.dumps(data, indent=2, sort_keys=True)

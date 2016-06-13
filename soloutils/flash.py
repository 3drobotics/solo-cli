"""
Performs a flash update of the Solo, Artoo, or both.  Software will not be
automatically downloaded unless the download argument is specified.
The total software update will take between 2 and 5 minutes, depending
on the internet connection and the number of components on the Solo/Artoo
that require updating.
"""

from __future__ import print_function
from datetime import datetime, timedelta
import sys, urllib2, re, urlparse, soloutils, time, base64
import socket
import posixpath
import hashlib
import json
import os
from scp import SCPClient
from distutils.version import LooseVersion

SERVERADDR = 'http://firmwarehouse.3dr.com/'
TOKEN = '51fbe08cf5ef0800a07af051031a21d7f9f5438e'

def errprinter(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class FirmwareRelease(object):
    def __init__(self, json):
        self.version = json['major'] + '.' + json['minor'] + '.' + json['patch']
        if 'suffix' in json and json['suffix']:
            self.version += '-' + json['suffix']
        self.url = json['file']
        self.md5 = json['md5']
        self.channel = json['channel']
        self.product = json['product']

def openurl(url):
    request = urllib2.Request(url)
    request.add_header('Authorization', 'Token ' + TOKEN)
    return urllib2.urlopen(request)

def releases(product, channels):
    results = []
    url = urlparse.urljoin(SERVERADDR, 'releases/')
    while True:
        parsed = json.loads(openurl(url).read())
        results += parsed['results']
        if parsed['next']:
            url = parsed['next']
        else:
            break
    return sorted(filter(lambda x: x.product in product and (x.channel in channels if ('SOLO_UNFILTERED_UPDATES' in os.environ) else x.channel == 1), map(FirmwareRelease, results)), key=lambda x: LooseVersion(x.version))

def fetch(release):
    import requests

    file_name = release.url.split('/')[-1]
    u = requests.get(release.url, stream=True)
    f = open('/tmp/' + file_name, 'wb')
    file_size = int(u.headers['Content-Length'])
    errprinter("downloading: %s Bytes: %s" % (file_name, file_size))
    errprinter("        url: %s" % (release.url,))

    sig = hashlib.md5()

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.raw.read(block_sz)
        if not buffer:
            break

        sig.update(buffer)
        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        errprinter(status, end='')

    f.close()
    errprinter('')

    f2 = open('/tmp/' + file_name + '.md5', 'wb')
    f2.write(release.md5 + '  ' + file_name + '\n')
    f2.close()

    if release.md5 != sig.hexdigest():
        errprinter('expected md5 of {}, received file with md5 of {}'.format(md5, sig.hexdigest()))
        errprinter('please check the file {}'.format(url))
        errprinter('and try again.')
        sys.exit(1)

    return '/tmp/' + file_name, '/tmp/' + file_name + '.md5'

def list():
    errprinter('checking Internet connectivity...')
    soloutils.await_net()

    controller = releases([1, 10], [1, 7])
    drone = releases([2, 9], [1, 7])

    for update in controller:
        print('controller', update.version)
    for update in drone:
        print('drone', update.version)

    sys.exit(0)

def clean_settings(args):
    if args['both']:
        group = 'Solo and the Controller'
    if args['drone']:
        group = 'Solo'
    if args['controller']:
        group = 'the Controller'

    print('connecting to {}...'.format(group))

    if args['drone'] or args['both']:
        solo = soloutils.connect_solo(await=True)
    if args['controller'] or args['both']:
        controller = soloutils.connect_controller(await=True)

    if args['drone'] or args['both']:
        soloutils.settings_reset(solo)
        print('Solo will delete user files once it reboots.')
    if args['controller'] or args['both']:
        newstyle = soloutils.settings_reset(controller)
        print('Controller will delete user files once it reboots.')

    dt = datetime.today() + timedelta(minutes=4)
    print('please wait up to four minutes longer for the process to complete (by {}).'.format(dt.strftime('%-I:%M')))

    if args['drone'] or args['both']:
        solo.close()
    if args['controller'] or args['both']:
        controller.close()

    sys.exit(0)

def factory_reset(args):
    if args['both']:
        group = 'Solo and the Controller'
    if args['drone']:
        group = 'Solo'
    if args['controller']:
        group = 'the Controller'

    print('connecting to {}...'.format(group))

    if args['drone'] or args['both']:
        solo = soloutils.connect_solo(await=True)
    if args['controller'] or args['both']:
        controller = soloutils.connect_controller(await=True)

    if args['drone'] or args['both']:
        soloutils.factory_reset(solo)
        print('Solo will restore to factory version once it reboots.')
    if args['controller'] or args['both']:
        newstyle = soloutils.factory_reset(controller)
        print('Controller will restore to factory version once it reboots.')

    dt = datetime.today() + timedelta(minutes=4)
    print('please wait up to four minutes longer for the process to complete (by {}).'.format(dt.strftime('%-I:%M')))

    if args['drone'] or args['both']:
        solo.close()
    if args['controller'] or args['both']:
        controller.close()

    sys.exit(0)

def flash(target, firmware_file, firmware_md5, args):
    # Connect to controller...
    if target == 'controller':
        errprinter('connecting to Controller...')
        client = soloutils.connect_controller(await=True)
    else:
        errprinter('connecting to Solo...')
        client = soloutils.connect_solo(await=True)

    # Prepare the update.
    # older versions don't have sololink_config and ssh returns 127, so do it manually
    code = soloutils.command_stream(client, 'sololink_config --update-prepare sololink')
    if code != 0:
        soloutils.command_stream(client, 'rm -rf /log/updates && mkdir -p /log/updates')

    # Upload the files.
    errprinter('uploading files...')
    scp = SCPClient(client.get_transport())
    scp.put(firmware_file, posixpath.join('/log/updates/', posixpath.basename(firmware_file)))
    scp.put(firmware_md5, posixpath.join('/log/updates/', posixpath.basename(firmware_md5)))
    scp.close()

    if target == 'controller':
        errprinter("starting update on the Controller...")
    else:
        errprinter("starting update on Solo...")

    if args['--clean']:
        errprinter('marking all user-local changes to be reset...')
        code = soloutils.command_stream(client, 'sololink_config --update-apply sololink --reset')
    else:
        code = soloutils.command_stream(client, 'sololink_config --update-apply sololink')
    # Fallback to earlier versions.
    if code != 0:
        if args['--clean']:
            code = soloutils.command_stream(client, 'touch /log/updates/UPDATE && touch /log/updates/RESETSETTINGS && shutdown -r now')
        else:
            code = soloutils.command_stream(client, 'touch /log/updates/UPDATE && shutdown -r now')

    if target == 'controller':
        errprinter('the Controller will update once it reboots!')
    else:
        errprinter('Solo will update once it reboots!')

    dt = datetime.today() + timedelta(minutes=4)
    errprinter('please wait up to four minutes longer for the installation to complete (by {}).'.format(dt.strftime('%-I:%M')))

    # Complete!
    client.close()

    return code

def flash_px4(firmware_file):
    errprinter('connecting to Solo...')
    client = soloutils.connect_solo(await=True)
    soloutils.command_stream(client, 'rm -rf /firmware/loaded')

    # Upload the files.
    errprinter('uploading files...')
    scp = SCPClient(client.get_transport())
    scp.put(firmware_file, '/firmware')
    scp.close()

    # shutdown solo for firmware reflash
    #code = soloutils.command_stream(client, 'shutdown -r now')
    code = soloutils.command_stream(client, 'loadPixhawk.py')
    #errprinter('Solo will update once it reboots!')
    errprinter('Pixhawk has been updated to new firmware')
    #dt = datetime.today() + timedelta(minutes=4)
    #errprinter('please wait up to four minutes longer for the installation to complete (by {}).'.format(dt.strftime('%-I:%M')))

    # Complete!
    client.close()

    sys.exit(0)

def download_firmware(target, version):
    if target == 'controller':
        product = [1, 10]
    else:
        product = [2, 9]

    updates = releases(product, [1, 7])

    if version:
        updates = filter(lambda x: version in re.sub('.tar.gz', '', x.url.split('/')[-1]), updates)
        if len(updates) == 0:
            errprinter('error: no version matching {} were found.'.format(version))
            sys.exit(1)

    return fetch(updates[-1])

def main(args):
    if args['--list']:
        list()
        return

    if args['pixhawk']:
        if args['<filename>']:
            firmware_file = args['<filename>']
            flash_px4(firmware_file)
    	return

    if args['both']:
        group = 'Solo and the Controller'
    if args['drone']:
        group = 'Solo'
    if args['controller']:
        group = 'the Controller'

    version = None
    local_file = None
    if args['<version>']:
        if re.match(r'^[./]', args['<version>']):
            local_file = args['<version>']
        else:
            version = re.sub(r'^v', '', args['<version>'])
            if not re.match(r'^\d+', version):
                errprinter('error: verion number specified looks invalid.')
                sys.exit(1)

    # Specific exceptions to the update flow.
    if args['current'] and not args['--clean']:
        # solo flash XXX current
        errprinter('you are already flashed at your current version. stopping.')
        sys.exit(0)
    if args['factory'] and not args['--clean']:
        # solo flash XXX factory
        errprinter('error: cannot reset to factory firmware without specifying --clean.')
        sys.exit(1)

    # prompt for consent
    errprinter('you are about to flash {}.'.format(group))
    if args['--clean']:
        errprinter('by specifying --clean, you will REMOVE ALL LOCAL CHANGES to Solo.')
    else:
        errprinter('this PRESERVES ALL LOCAL CHANGES to Solo, but any conflicts')
        errprinter('with newer updates is not guaranteed to work.')

    y = raw_input('proceed to perform update? [y/N] ')
    if not (y.lower() == 'y' or y.lower() == 'yes'):
        sys.exit(1)

    # Specific exceptions to the update flow.
    if args['current'] and args['--clean']:
        # solo flash XXX current --clean
        return clean_settings(args)
    if args['factory'] and args['--clean']:
        # solo flash XXX factory --clean
        return factory_reset(args)

    if local_file:
        if args['both']:
            errprinter('you must specify drone or controller separately, not both, with local files.')
            sys.exit(1)

        controller_file = drone_file = os.path.abspath(local_file)
        controller_md5 = drone_md5 = os.path.abspath(local_file) + '.md5'
    else:
        errprinter('')
        errprinter('checking Internet connectivity...')
        soloutils.await_net()

        if args['drone'] or args['both']:
            drone_file, drone_md5 = download_firmware('drone', version)
        if args['controller'] or args['both']:
            controller_file, controller_md5 = download_firmware('controller', version)

    errprinter('')
    errprinter('please power on ' + group + ' and connect your computer')
    errprinter('to Solo\'s wifi network.')

    errprinter('')
    if args['drone'] or args['both']:
        code = flash('drone', drone_file, drone_md5, args)
    if args['both']:
        errprinter('')
    if args['controller'] or args['both']:
        code = flash('controller', controller_file, controller_md5, args)
        if code != 0:
            sys.exit(code)

    sys.exit(code)

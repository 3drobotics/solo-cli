"""
Performs an update of the Solo, Artoo, or both.  Software will not be
automatically downloaded unless the download argument is specified.
The total software update will take between 2 and 5 minutes, depending
on the internet connection and the number of components on the Solo/Artoo
that require updating.
"""

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

class FirmwareRelease(object):
    def __init__(self, json):
        self.version = json['major'] + '.' + json['minor'] + '.' + json['patch']
        self.url = json['file']
        self.md5 = json['md5']
        self.channel = json['channel']
        self.product = json['product']

def openurl(url):
    request = urllib2.Request(url)
    request.add_header('Authorization', 'Token ' + TOKEN)
    return urllib2.urlopen(request)

def releases(product):
    results = []
    url = urlparse.urljoin(SERVERADDR, 'releases/')
    while True:
        parsed = json.loads(openurl(url).read())
        results += parsed['results']
        if parsed['next']:
            url = parsed['next']
        else:
            break
    return sorted(filter(lambda x: x.product in product and ('SOLO_UNFILTERED_UPDATES' in os.environ or x.channel == 1), map(FirmwareRelease, results)), key=lambda x: LooseVersion(x.version))

def fetch(release):
    import requests

    file_name = release.url.split('/')[-1]
    u = requests.get(release.url, stream=True)
    f = open('/tmp/' + file_name, 'wb')
    file_size = int(u.headers['Content-Length'])
    print "downloading: %s Bytes: %s" % (file_name, file_size)

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
        print status,

    f.close()
    print ''

    f2 = open('/tmp/' + file_name + '.md5', 'wb')
    f2.write(release.md5 + '  ' + file_name + '\n')
    f2.close()

    if release.md5 != sig.hexdigest():
        print 'expected md5 of {}, received file with md5 of {}'.format(md5, sig.hexdigest())
        print 'please check the file {}'.format(url)
        print 'and try again.'
        sys.exit(1)

    return '/tmp/' + file_name, '/tmp/' + file_name + '.md5'

def main(args):
    if args['both']:
        group = 'Solo and the Controller'
    if args['solo']:
        group = 'Solo'
    if args['controller']:
        group = 'the Controller'

    version = None
    if args['<version>']:
        version = re.sub(r'^v', '', args['<version>'])
        if not re.match(r'^\d+', version):
            print 'error: verion number specified looks invalid.'
            sys.exit(1)

    # prompt for consent
    print 'you are about to update {}.'.format(group)
    print 'this preserves all your local changes to Solo, but compatibility'
    print 'with newer updates is not guaranteed.'
    y = raw_input('proceed to perform update? [y/N] ')
    if not (y.lower() == 'y' or y.lower() == 'yes'):
        sys.exit(1)

    if not args['latest'] and not version:
        print 'TODO: only solo update to "latest" or "<version>" works yet.'
        sys.exit(1)
    if args['both']:
        print 'TODO: only "solo" or "controller" update yet works, not "both".'
        sys.exit(1)

    print 'waiting for Internet connectivity...'
    soloutils.await_net()

    if args['controller']:
        product = [1, 10]
    else:
        product = [2, 9]

    updates = releases(product)

    if version:
        updates = filter(lambda x: version in re.sub('.tar.gz', '', x.url.split('/')[-1]), updates)
        if len(updates) == 0:
            print 'error: no version matching {} were found.'.format(version)
            sys.exit(1)
    file_loc, md5_loc = fetch(updates[-1])

    print 'please power-up the Controller and connect your PC to the Solo wifi network.'

    # Connect to controller...
    if args['controller']:
        print 'connecting to Controller...'
        client = soloutils.connect_controller(await=True)
    else:
        print 'connecting to Solo...'
        client = soloutils.connect_solo(await=True)

    # Prepare the update.
    # older versions don't have sololink_config and ssh returns 127, so do it manually
    code = soloutils.command_stream(client, 'sololink_config --update-prepare sololink')
    if code != 0:
        soloutils.command_stream(client, 'rm -rf /log/updates && mkdir -p /log/updates')

    # Upload the files.
    print 'uploading updates...'
    scp = SCPClient(client.get_transport())
    scp.put(file_loc, posixpath.join('/log/updates/', posixpath.basename(file_loc)))
    scp.put(md5_loc, posixpath.join('/log/updates/', posixpath.basename(md5_loc)))
    scp.close()

    if args['controller']:
        print "starting update on the Controller..."
    else:
        print "starting update on Solo..."
    code = soloutils.command_stream(client, 'sololink_config --update-apply sololink')
    if code != 0:
        code = soloutils.command_stream(client, 'touch /log/updates/UPDATE && shutdown -r now')
        if args['controller']:
            print('the Controller will update once it reboots.')
        else:
            print('Solo will update once it reboots.')
    else:
        print('update succeeded!')

    dt = datetime.today() + timedelta(minutes=3, seconds=20)
    print('please wait up to three minutes longer for the installation to complete (by {}).'.format(dt.strftime('%-I:%M %p')))

    # Complete!
    client.close()
    sys.exit(code)

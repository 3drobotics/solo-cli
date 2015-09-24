"""
Performs an update of the Solo, Artoo, or both.  Software will not be
automatically downloaded unless the download argument is specified.
The total software update will take between 2 and 5 minutes, depending
on the internet connection and the number of components on the Solo/Artoo
that require updating.
"""

from datetime import datetime, timedelta
import sys, urllib2, re, urlparse, soloutils, time, base64, requests
import socket
import posixpath
import hashlib
from scp import SCPClient
from distutils.version import LooseVersion

SERVERADDR = '***REMOVED***'
USERNAME = 'sololink'
PASSWORD = '***REMOVED***'

def openurl(url):
    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (USERNAME, PASSWORD)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    return urllib2.urlopen(request)

def releases(where):
    root = urlparse.urljoin(urlparse.urljoin(SERVERADDR, where), 'update/')
    listing = openurl(root).read()
    releases = list(set(re.findall(r'[^">]+.tar.gz', listing)))
    releases.sort(key=LooseVersion)
    return releases

def fetch(where, filename):
    root = urlparse.urljoin(urlparse.urljoin(SERVERADDR, where), 'update/')
    url = urlparse.urljoin(root, filename)

    # Download MD5 file
    md5 = openurl(url + '.md5').read()

    file_name = url.split('/')[-1]
    u = openurl(url)
    f = open('/tmp/' + file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "downloading: %s Bytes: %s" % (file_name, file_size)

    sig = hashlib.md5()

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
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
    f2.write(md5)
    f2.close()

    if md5.split()[0] != sig.hexdigest():
        print 'expected md5 of {}, received file with md5 of {}'.format(md5, sig.hexdigest())
        print 'please check the file {}'.format(url)
        print 'and try again.'
        sys.exit(1)

    return '/tmp/' + file_name, '/tmp/' + file_name + '.md5'

def await_net():
    socket.setdefaulttimeout(5)
    while True:
        try:
            socket.gethostbyname(urlparse.urlparse(SERVERADDR).hostname)
        except KeyboardInterrupt as e:
            raise e
        except:
            time.sleep(0.1)
            continue

        try:
            response = openurl(SERVERADDR)
        except KeyboardInterrupt as e:
            raise e
        except:
            time.sleep(0.1)
            continue
        else:
            break

def main(args):
    # board1080=0
    # if [ $artooonly == 0 ]; then
    #     while true; do
    #         read -p "Are you using a production Sololink board (y/n)?" yn
    #         case $yn in
    #             [Yy]* ) board1080=1; break;;
    #             [Nn]* ) break;;
    #             * ) echo "Please answer yes or no.";;
    #         esac
    #     done
    # fi

    if args['both']:
        group = 'Solo and the Controller'
    if args['solo']:
        group = 'Solo'
    if args['controller']:
        group = 'the Controller'

    # prompt for consent
    print 'you are about to update {}.'.format(group)
    print 'this preserves all your local changes to Solo, but compatibility'
    print 'with newer updates is not guaranteed.'
    y = raw_input('proceed to perform update? [y/N] ')
    if not (y.lower() == 'y' or y.lower() == 'yes'):
        sys.exit(1)

    if not args['latest']:
        print 'TODO: only solo update to "latest" works yet.'
        sys.exit(1)
    if args['both']:
        print 'TODO: only "solo" or "controller" update yet works, not "both".'
        sys.exit(1)

    print 'waiting for Internet connectivity...'
    await_net()

    if args['controller']:
        updatepath = 'artoo/digital/'
    else:
        updatepath = 'solo/1080p/'

    updates = releases(updatepath)
    file_loc, md5_loc = fetch(updatepath, updates[-1])

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

    dt = datetime.today() + timedelta(minutes=4)
    print('please wait up to three minutes longer for the installation to complete (at {}).'.format(dt.strftime('%-I:%M')))

    # Complete!
    client.close()
    sys.exit(code)

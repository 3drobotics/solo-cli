import paramiko, base64, time, sys
import os
import soloutils
from distutils.version import LooseVersion
from scp import SCPClient
import posixpath
import hashlib

SCRIPT_FILENAME = 'solo-script.tar.gz'

def push(solo, scp, force):
    if not force:
        code, stdout, stderr = soloutils.command(solo, 'md5sum /tmp/solo-script.tar.gz')
        md5sum = next(iter((stdout or '').split()), None)
        localmd5sum = hashlib.md5(open(SCRIPT_FILENAME, 'rb').read()).hexdigest()
        
        if code == 0 and md5sum == localmd5sum:
            print 'script bundle already up to date.'
            return 0

    print 'uploading script bundle...'
    scp.put(SCRIPT_FILENAME, '/tmp')
    return soloutils.command_stream(solo, '''
set -e
rm -rf /log/solo-script || true
mkdir /log/solo-script
cd /log/solo-script
tar -xvf /tmp/solo-script.tar.gz
virtualenv --clear env || virtualenv env
source ./env/bin/activate
pip install --no-index -UI ./wheelhouse/* 
''')

def push_main(args):
    if not os.path.exists(SCRIPT_FILENAME):
        print 'ERROR: Please run "solo script pack" first to bundle your archive.'
        return 1

    print 'connecting to solo...'
    solo = soloutils.connect_solo(await=True)
    scp = SCPClient(solo.get_transport())

    # Requires pip
    print 'checking pip...'
    if soloutils.install_pip.run(solo, scp) != 0:
        print 'failed installing pip.'
        sys.exit(1)

    # TODO check args['<arg>'] for --force

    push(solo, scp, '--force' in args['<arg>'])

    scp.close()
    solo.close()

def run_main(args):
    if not os.path.exists(SCRIPT_FILENAME):
        print 'ERROR: Please run "solo script pack" first to bundle your archive.'
        return 1

    print 'connecting to solo...'
    solo = soloutils.connect_solo(await=True)
    scp = SCPClient(solo.get_transport())

    # Requires pip
    print 'checking pip...'
    if soloutils.install_pip.run(solo, scp) != 0:
        print 'failed installing pip.'
        sys.exit(1)

    push(solo, scp, '--force' in args['<arg>'])

    print 'running script...'
    print ''
    soloutils.command_stream(solo, '''
set -e
cd /log/solo-script
source ./env/bin/activate
exec python /log/solo-script/''' + args['<arg>'][1]  + '''
''')

    scp.close()
    solo.close()

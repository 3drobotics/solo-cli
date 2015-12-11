import paramiko, base64, time, sys
import os
import soloutils
from distutils.version import LooseVersion
from scp import SCPClient
import posixpath

# This script operates in two stages: creating the script file
# and then executing it, so we are resilient to network dropouts.

SCRIPT = """
pip --version 2>/dev/null
if [ $? == 0 ]; then
    echo 'pip is installed on Solo.'
    exit 0
fi

python -c "import urllib2; print urllib2.urlopen('https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py').read()" | python
pip install pip --upgrade

echo ''
pip --version
echo 'pip is installed on Solo.'
"""

def main(args):
    print 'connecting to solo...'
    solo = soloutils.connect_solo(await=True)
    scp = SCPClient(solo.get_transport())

    code, stdout, stderr = soloutils.command(solo, 'pip --version')
    if code != 0:
        print 'installing pip... ',
        scp.put(os.path.join(os.path.dirname(__file__), '../lib/ez_setup.py'), '/tmp')
        scp.put(os.path.join(os.path.dirname(__file__), '../lib/setuptools-18.7.1.zip'), '/tmp')
        code, stdout, stderr = soloutils.command(solo, 'cd /tmp; python ez_setup.py --to-dir=/tmp')
        if code:
            print ''
            print 'Error in installing pip:'
            print stdout
            print stderr
            sys.exit(1)
        print 'done.'

    code, stdout, stderr = soloutils.command(solo, 'python -c "import wheel"')
    if code != 0:
        print 'installing wheel... ',
        scp.put(os.path.join(os.path.dirname(__file__), '../lib/wheel-0.26.0.tar.gz'), '/tmp')
        code, stdout, stderr = soloutils.command(solo, 'pip install /tmp/wheel-0.26.0.tar.gz')
        if code:
            print ''
            print 'Error in installing wheel:'
            print stdout
            print stderr
            sys.exit(1)
        print 'done.'

    code, stdout, stderr = soloutils.command(solo, 'virtualenv --version')
    if code != 0:
        print 'installing virtualenv... ',
        scp.put(os.path.join(os.path.dirname(__file__), '../lib/virtualenv-13.1.2.tar.gz'), '/tmp')
        code, stdout, stderr = soloutils.command(solo, 'pip install /tmp/virtualenv-13.1.2.tar.gz')
        if code:
            print ''
            print 'Error in installing virtualenv:'
            print stdout
            print stderr
            sys.exit(1)
        print 'done.'

    scp.close()
    solo.close()

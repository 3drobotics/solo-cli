import paramiko, base64, time, sys, soloutils
from distutils.version import LooseVersion

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
    print 'NOTE: this process requires simultaneous access to'
    print 'Solo and to the Internet. if you have not yet done so,'
    print 'run `solo wifi` to connect to Solo and to a local'
    print 'wifi connection simultaneously.'
    print ''

    print 'connecting to solo...'
    solo = soloutils.connect_solo(await=True)

    print 'waiting for Internet connectivity...'
    soloutils.await_net()

    print ''
    code = soloutils.command_stream(solo, SCRIPT)
    solo.close()
    sys.exit(code)

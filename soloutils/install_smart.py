import paramiko, base64, time, sys, soloutils
from distutils.version import LooseVersion

SCRIPT = """
# Patch smart to allow --remove-all
# See http://lists.openembedded.org/pipermail/openembedded-core/2014-July/095090.html
# But ather than reinstall smart, just patch the Python code
sed -i.bak 's/, \"remove-all\",/, \"remove_all\",/g' /usr/lib/python2.7/site-packages/smart/commands/channel.py

PACKAGE_URL="http://solo-packages.s3-website-us-east-1.amazonaws.com"

printf 'setting up repositories.'; smart channel --remove-all -y 2>&1 | xargs
printf 'rpmsys...'; smart channel --add rpmsys type=rpm-sys name='RPM Database' -y
printf 'all...'; smart channel --add all type=rpm-md baseurl=$PACKAGE_URL/3.10.17-rt12/all/ -y
printf 'cortexa9hf_vfp_neon...'; smart channel --add cortexa9hf_vfp_neon type=rpm-md baseurl=$PACKAGE_URL/3.10.17-rt12/cortexa9hf_vfp_neon/ -y
printf 'cortexa9hf_vfp_neon_mx6...'; smart channel --add cortexa9hf_vfp_neon_mx6 type=rpm-md baseurl=$PACKAGE_URL/3.10.17-rt12/cortexa9hf_vfp_neon_mx6/ -y
printf 'imx6solo_3dr_1080p...'; smart channel --add imx6solo_3dr_1080p type=rpm-md baseurl=$PACKAGE_URL/3.10.17-rt12/imx6solo_3dr_1080p/ -y

echo ''
smart update

echo ''
echo 'smart package manager is now ready to use.'
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

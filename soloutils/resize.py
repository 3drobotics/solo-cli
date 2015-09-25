import paramiko, base64, time, sys, soloutils
from datetime import datetime, timedelta
from distutils.version import LooseVersion

# This script operates in two stages: creating the script file
# and then executing it, so we are resilient to network dropouts.

SCRIPT = """
cat > /tmp/soloutils.sh << 'SCRIPT'

echo 'installing packages...'
smart install parted libss2 e2fsprogs e2fsprogs-badblocks e2fsprogs-mke2fs lsof -y

echo ''
echo 'resizing partitions...'

# Solo has four partitions:
# /dev/mmcblk0p1
# /dev/mmcblk0p2
# /dev/mmcblk0p3 - root linux parition
# /dev/mmcblk0p4 - log partition

# We need to stop anything which is writing to /log
# or else we can't resize its filesystem.

# Drop the runlevel to 3 (disabling Solo services)
init 2
killall runsv
if [ -e /dev/mmcblk0p4 ]; then
    # Then stop syslog.
    /etc/init.d/syslog stop
    sleep 1
    # Finally, we can unmount /log
    umount /log || { { umount /log | grep "not mounted"; } && exit 1; }
fi

# We will DANGEROUSLY go ahead and resize the root
# partition and shrink the log partition.
cat <<'EOF' | fdisk /dev/mmcblk0
d
4
d
3
n
p
3
391168
1800001
n
p
1800002
15523839
w
EOF

sleep 3

# After succeeding in changing our root partitions, we
# tell the OS to re-read the parition list.
partprobe /dev/mmcblk0

# We need to format our log partition, or otherwise
# it will not be recognized on startup.
mkfs.ext3 /dev/mmcblk0p4

# We also want to expand our root partition to fill the 
# available space.
resize2fs /dev/mmcblk0p3

# Finally we restart (for good measure?) and see that
# Solo sees our changes on next bootup.
echo 'shutting down...'
sleep 2
sync
sleep 2
init 4
sleep 5
shutdown -r now
SCRIPT

chmod +x /tmp/soloutils.sh
exec /tmp/soloutils.sh
"""

def main(args):
    print 'NOTE: this process requires simultaneous access to'
    print 'Solo and to the Internet. if you have not yet done so,'
    print 'run `solo wifi` to connect to Solo and to a local'
    print 'wifi connection simultaneously.'
    print ''
    print 'NOTE: also run `solo install-smart` first.'
    print ''

    # prompt for consent
    print 'WARNING: this can break your Solo and require a factory reset!'
    print 'your Solo will turn off after and you will need to power cycle it.'
    y = raw_input('proceed to resize filesystem? [y/N] ')
    if not (y.lower() == 'y' or y.lower() == 'yes'):
        sys.exit(1)

    print ''
    print 'connecting to solo...'
    solo = soloutils.connect_solo(await=True)

    print 'waiting for Internet connectivity...'
    soloutils.await_net()

    print ''
    code = soloutils.command_stream(solo, SCRIPT)

    print ''
    dt = datetime.today() + timedelta(minutes=4)
    print('please wait up to three minutes longer for the resize to complete (at {}).'.format(dt.strftime('%-I:%M')))
    print('(you can manually restart solo if it fails to come online again.)')

    solo.close()
    sys.exit(code)

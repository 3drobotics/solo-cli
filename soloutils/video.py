import paramiko, base64, time, sys, soloutils
from distutils.version import LooseVersion

ACQUIRE = """
echo 'acquiring video feed...'
if [ ! -e /usr/bin/video_send_logic.sh ]; then
    cp /usr/bin/video_send.sh /usr/bin/video_send_logic.sh
    echo '#!/bin/bash
if [ -e /home/root/ACQUIRE_VIDEO_FEED ]; then
    while true; do sleep 100000; done;
else
    exec /usr/bin/video_send_logic.sh
done' > /usr/bin/video_send.sh
}

touch ~/ACQUIRE_VIDEO_FEED
echo '/dev/video0 will be available for use by user scripts after reboot.'
echo 'rebooting...'
sync
sololink_config --reboot
"""

RESTORE = """
echo 'restoring video feed...'
rm ~/ACQUIRE_VIDEO_FEED 2> /dev/null
echo 'video feed will be restored after reboot.'
echo 'rebooting...'
sync
sololink_config --reboot
"""

def main(args):
    print 'connecting to solo...'
    solo = soloutils.connect_solo(await=True)

    if args['acquire']:
        code = soloutils.command_stream(solo, ACQUIRE)
    elif args['restore']:
        code = soloutils.command_stream(solo, RESTORE)

    solo.close()
    sys.exit(code)

import paramiko, base64, time, sys, soloutils
from distutils.version import LooseVersion

ACQUIRE = """
TOGGLE="if [ -e /home/root/ACQUIRE_VIDEO_FEED ]; then modprobe mxc_v4l2_capture; while true; do sleep 100000; done; fi"

echo 'acquiring video feed...'
grep -q "while true; do sleep 100000; done" /usr/bin/video_send.sh || {
    cp /usr/bin/video_send.sh /usr/bin/video_send.sh.bkp
    echo "#!/bin/sh" > /usr/bin/video_send.sh
    echo "$TOGGLE" >> /usr/bin/video_send.sh
    echo "" >> /usr/bin/video_send.sh
    cat /usr/bin/video_send.sh.bkp >> /usr/bin/video_send.sh
}

touch ~/ACQUIRE_VIDEO_FEED
killall video_send.sh sn_master_snd sn_sender sn_pktsnd gst-launch-0.10 2>/dev/null
init q
echo '/dev/video0 will be available for use by user scripts after reboot.'
echo 'rebooting...'
sync
reboot
"""

RESTORE = """
echo 'restoring video feed...'
rm ~/ACQUIRE_VIDEO_FEED 2> /dev/null
killall video_send.sh sn_master_snd sn_sender sn_pktsnd gst-launch-0.10 2>/dev/null
init q
echo '/dev/video0 reclaimed for the video downlink.'
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

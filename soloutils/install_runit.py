import paramiko, base64, time, sys, soloutils
from distutils.version import LooseVersion

SCRIPT = """
# This script will install runit as a process spawned by /etc/inittab
# to monitor services under /etc/solo-services under runlevel 4

need() {
    for var in "$@"; do
        which "$var" >/dev/null
        if [ $? != 0 ]; then
            return 1
        fi
    done
}

set -e

need "sv" || {
	cd /tmp
	smart download busybox
	rpm -iv --replacepkgs busybox-*
}

# This function ensures that a line exists in a given file.
# If it doesn't, it adds it.
lineinfile () {
    FILE=$1
    LINE=$2
    grep -q "$LINE" "$FILE" || echo "$LINE" >> "$FILE"
}

echo 'setting up /etc/solo-services directory...'

# First create the directory where our services will live.
mkdir -p /etc/solo-services

# We require a script called /sbin/solo-services-start.
# This will be launched on startup as a long-lived process
# (under runlevel 4) that monitors the /etc/solo-services
# directory and respawns services that live there.
# Lookup runsvdir(8) for more information on how this works.
cat <<'EOF' > /sbin/solo-services-start
#!/bin/sh
PATH=/usr/local/bin:/usr/local/sbin:/bin:/sbin:/usr/bin:/usr/sbin:/usr/X11R6/bin
exec env - PATH=$PATH \
runsvdir -P /etc/solo-services "log: $(printf '.%.0s' {1..395})"
EOF
chmod +x /sbin/solo-services-start

# We add /sbin/solo-services-start as a startup script.
lineinfile "/etc/inittab" "SSS:4:respawn:/sbin/solo-services-start"
echo "export SVDIR=/etc/solo-services" > /etc/profile.d/solo-services

# Tell the OS to re-read /etc/inittab and immediately
# launch all services.
init q

echo ''
echo 'runit is now ready to use.'
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

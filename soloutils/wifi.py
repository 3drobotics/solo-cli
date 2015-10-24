import paramiko, base64, time, sys, soloutils
from distutils.version import LooseVersion

# This script operates in two stages: creating the script file
# and then executing it, so we are resilient to network dropouts.

SCRIPT3 = """
wget -O- http://example.com/ --timeout=5 >/dev/null 2>&1
"""

SCRIPT2 = """
cat > /tmp/align_channel.py <<'SCRIPT'
import itertools, re, subprocess
from pprint import pprint
import sys, time

# align_channel.py 3DR

if len(sys.argv) < 2:
    print 'Usage: align_channel.py <ssid>'
    sys.exit(1)

def build_tree(data):
    lines = data.split('\\n')

    stack = [[]]
    indent = ['']
    i = 0
    while i < len(lines):
        line = lines[i]
        if line[:len(indent[0])] == indent[0]:
            leadtab = line[len(indent[0]):len(indent[0]) + 1]
            if leadtab == '\\t':
                stack.insert(0, [])
                indent.insert(0, indent[0] + leadtab)
            sub = line[len(indent[0]):]
            if len(sub):
                stack[0].append(line[len(indent[0]):])
            i += 1
        else:
            last = stack.pop(0)

            # Tabs can roll onto previous line if short enough
            if stack[0][-1] and '\\t' in stack[0][-1]:
                a = stack[0][-1].split('\\t')
                stack[0][-1] = a[0] or ''
                last.insert(0, a[1] or '')

            stack[0].append(last)
            indent.pop(0)

    return stack.pop()

input = subprocess.check_output('iw dev wlan0 scan ap-force', shell=True)
networks = []
for entry in build_tree(input):
    if not isinstance(entry, basestring):
        ssid = None
        freq = None
        for e in entry:
            if isinstance(e, basestring):
                if 'SSID' in e:
                    try:
                        ssid = e.split(None, 2)[1]
                    except:
                        pass
                if 'freq' in e:
                    try:
                        freq = e.split(None, 2)[1]
                    except:
                        pass
        networks.append((ssid, freq))

input = subprocess.check_output('iw dev', shell=True)
curfreq = None
noht = None
for phy in build_tree(input):
    if not isinstance(phy, basestring):
        for i in xrange(0, len(phy)):
            if isinstance(phy[i], basestring) and 'wlan0-ap' in phy[i]:
                try:
                    curfreq = re.search(r'(\d+) [Mm][Hh][Zz]', '\\n'.join(phy[i+1])).group(1)
                except:
                    pass
                noht = re.search(r'[Nn][Oo] HT', '\\n'.join(phy[i+1]))

if not curfreq:
    print 'Could not identify current frequency, trying anyway...'

targetfreq = None
for (S, M) in networks:
    if S == sys.argv[1]:
        if not targetfreq or targetfreq != curfreq:
            targetfreq = M

if not targetfreq:
    print 'Specified SSID not found. Are you sure it was typed correctly?'
    sys.exit(1)

print 'current frequency: ' + curfreq
print 'target frequency: ' + targetfreq
sys.stdout.flush()
time.sleep(1)

if curfreq != targetfreq:
    input = subprocess.check_output('hostapd_cli chan_switch 1 ' + str(targetfreq) + (' ht' if not noht else ''), shell=True)

print '(Target frequency matched.)'
SCRIPT

ifconfig wlan0 up
sleep 3
python /tmp/align_channel.py {ssid}
"""

SCRIPT = """
cat > /tmp/setupwifi.sh << 'SCRIPT'


cat <<EOF > /etc/wpa_client.conf
network={{
ssid="{ssid}"
psk="{password}"
}}
EOF

echo 1 > /proc/sys/net/ipv4/ip_forward

sed -i.bak 's/dhcp-option=3.*/dhcp-option=3,10.1.1.1/g' /etc/dnsmasq.conf
sed -i.bak 's/dhcp-option=6.*/dhcp-option=6,8.8.8.8/g' /etc/dnsmasq.conf

/etc/init.d/dnsmasq restart
sleep 2

echo 'connecting to the internet...'
wpa_supplicant -i wlan0 -c /etc/wpa_client.conf -B
udhcpc -i wlan0

sleep 3
wget -O- http://example.com/ --timeout=5 >/dev/null 2>&1 || {{
    echo 'no internet connection available!'
    echo 'check your wifi credentials and try again.'
    exit 1
}}

echo 'setting up IP forwarding...'
insmod /lib/modules/3.10.17-rt12-*/kernel/net/ipv4/netfilter/iptable_filter.ko
iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
iptables -A FORWARD -i wlan0 -o wlan0-ap -j ACCEPT
iptables -A FORWARD -i wlan0-ap -o wlan0 -j ACCEPT
SCRIPT

chmod +x /tmp/setupwifi.sh
/tmp/setupwifi.sh
"""

def main(args):
    print 'connecting to the Controller...'
    controller = soloutils.connect_controller(await=True)

    controller_version = soloutils.controller_versions(controller)['version']
    if LooseVersion('1.2.0') > LooseVersion(controller_version):
        print 'error: expecting Controller to be >= 1.2.0'
        print 'your Controller version: {}'.format(controller_version)
        print 'please flash your Controller with a newer version to run this command.'
        print ''
        print '    solo update solo latest'
        print '    solo update controller latest'
        sys.exit(1)

    print 'checking for wifi...'
    code = soloutils.command_stream(controller, SCRIPT3)

    if code == 0:
        print 'wifi already connected!'
        print "(if you are not connected to the Internet on your PC,"
        print " try to disconnect and reconnect to Solo\'s network.)"
        sys.exit(code)

    print 'switching to proper channel...'
    code = soloutils.command_blind(controller, SCRIPT2.format(ssid=args['--name']))
    time.sleep(10)
    controller.close()

    print ''
    print 'please disable and renable your WiFi.  then reconnect to Solo\'s network.'
    print '(this next step may take up to 60s.)'

    controller = soloutils.connect_controller(await=True)
    code = soloutils.command_stream(controller, SCRIPT.format(ssid=args['--name'], password=args['--password']))
    
    controller.close()

    if code == 0:
        try:
            print 'resetting Solo\'s wifi...'
            print '(if solo is not online, you can hit Ctrl+C safely now.)'
            solo = soloutils.connect_solo(await=True)
            soloutils.command_stream(solo, 'init 2 && init 4')
            solo.close()
        except KeyboardInterrupt:
            pass

        print ''
        print 'setup complete! you are now connected to the Internet.'
        print "(if you are not connected to the Internet on your PC,"
        print " try to disconnect and reconnect to Solo\'s network.)"

    sys.exit(code)

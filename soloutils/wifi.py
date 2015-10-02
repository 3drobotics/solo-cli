import paramiko, base64, time, sys, soloutils
from distutils.version import LooseVersion

# This script operates in two stages: creating the script file
# and then executing it, so we are resilient to network dropouts.

SCRIPT = """
cat > /tmp/setupwifi.sh << 'SCRIPT'

wget -O- http://example.com/ --timeout=5 >/dev/null 2>&1
if [ $? != 0 ]; then
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

    wpa_supplicant -i wlan0 -c /etc/wpa_client.conf -B
    udhcpc -i wlan0

    sleep 3
    wget -O- http://example.com/ --timeout=5 >/dev/null 2>&1 || {{
        echo 'no internet connection available!'
        echo 'check your wifi credentials and try again.'
        exit 1
    }}
fi

echo 'connecting to the internet...'

smart query --installed | grep 'kernel-module-iptable-filter' >/dev/null 2>&1
if [ $? != 0 ]; then
    python -c "import urllib2, sys; sys.stdout.write(urllib2.urlopen('https://s3.amazonaws.com/solo-packages/controller/kernel-module-iptable-filter-3.10.17-r0.imx6solo_3dr_artoo.rpm').read()); sys.stdout.flush()" > /tmp/iptable_filter.rpm
    rpm -iv --replacepkgs /tmp/iptable_filter.rpm
fi
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
    if LooseVersion('1.1.15') > LooseVersion(controller_version):
        print 'error: expecting Controller to be at least version 1.1.15'
        print 'your Controller version: {}'.format(controller_version)
        print 'please update your Controller to run this command.'
        sys.exit(1)

    code = soloutils.command_stream(controller, SCRIPT.format(ssid=args['--name'], password=args['--password']))
    controller.close()

    if code == 0:
        print 'resetting Solo\'s wifi...'
        print '(if solo is not online, you can hit Ctrl+C safely now.)'
        solo = soloutils.connect_solo(await=True)
        soloutils.command_stream(solo, 'init 2 && init 4')
        solo.close()

        print 'setup complete! you are now connected to the Internet.'
        print "(if you are not connected to the Internet on your PC,"
        print " disconnect and reconnect to Solo\'s network.)"

    sys.exit(code)

"""Solo utilities.

Usage:
  solo tunnel --name=<n> --password=<p>

Options:
  -h --help        Show this screen.
  --name=<n>       WiFi network name.
  --password=<p>   WiFi password.

"""

import paramiko, base64, time, sys
import docopt
from docopt import docopt

args = docopt(__doc__, version='solo-utils 1.0')

SCRIPT = """
cat > /tmp/setupwifi.sh << 'SCRIPT'

wget -O- http://example.com/ --timeout=5 >/dev/null 2>&1 && {{
    echo 'already connected to the internet!'
    exit 0
}}

cat <<EOF > /etc/wpa_client.conf
network={{
  ssid="{ssid}"
  psk="{password}"
}}
EOF

sed -i.bak 's/dhcp-option=3.*/dhcp-option=3,10.1.1.1/g' /etc/dnsmasq.conf
sed -i.bak 's/dhcp-option=6.*/dhcp-option=6,8.8.8.8/g' /etc/dnsmasq.conf

/etc/init.d/dnsmasq restart
sleep 2

wpa_supplicant -i wlan0 -c /etc/wpa_client.conf -B
udhcpc -i wlan0

sleep 3
wget -O- http://example.com/ --timeout=5 >/dev/null 2>&1 || {{
    echo 'not connected to the internet.'
    echo 'check your credentials and try again.'
    exit 1
}}
echo 'you are now connected to the internet.'

smart check kernel-module-iptable-filter --installed >/dev/null 2>&1
if [ $? != 0 ]; then
    python -c "import urllib2, sys; sys.stdout.write(urllib2.urlopen('https://s3.amazonaws.com/solo-packages/controller/kernel-module-iptable-filter-3.10.17-r0.imx6solo_3dr_artoo.rpm').read()); sys.stdout.flush()" > /tmp/iptable_filter.rpm
    rpm -iv --replacepkgs /tmp/iptable_filter.rpm
fi

iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
iptables -A FORWARD -i wlan0 -o wlan0-ap -j ACCEPT
iptables -A FORWARD -i wlan0-ap -o wlan0 -j ACCEPT

echo 'setup complete.'
SCRIPT

chmod +x /tmp/setupwifi.sh
/tmp/setupwifi.sh
""".format(ssid=args['--name'], password=args['--password'])

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.1.1.1', username='root', password='TjSDBkAu')

chan = client.get_transport().open_session()
chan.exec_command(SCRIPT)
while True:
    time.sleep(0.1)
    if chan.recv_ready():
        sys.stdout.write(chan.recv(4096).decode('ascii'))
    if chan.recv_stderr_ready():
        sys.stderr.write(chan.recv_stderr(4096).decode('ascii'))
    if chan.exit_status_ready():
        break

code = chan.recv_exit_status()
client.close()
sys.exit(code)

import itertools, re, subprocess
from pprint import pprint
import sys

# align_channel.py 3DR

if len(sys.argv) < 2:
    print 'Usage: align_channel.py <ssid>'
    sys.exit(1)

def build_tree(data):
    lines = data.split('\n')

    stack = [[]]
    indent = ['']
    i = 0
    while i < len(lines):
        line = lines[i]
        if line[:len(indent[0])] == indent[0]:
            leadtab = line[len(indent[0]):len(indent[0]) + 1]
            if leadtab == '\t':
                stack.insert(0, [])
                indent.insert(0, indent[0] + leadtab)
            sub = line[len(indent[0]):]
            if len(sub):
                stack[0].append(line[len(indent[0]):])
            i += 1
        else:
            last = stack.pop(0)

            # Tabs can roll onto previous line if short enough
            if stack[0][-1] and '\t' in stack[0][-1]:
                a = stack[0][-1].split('\t')
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

print networks

input = subprocess.check_output('iw dev', shell=True)
curfreq = None
noht = None
for phy in build_tree(input):
    if not isinstance(phy, basestring):
        for i in xrange(0, len(phy)):
            if isinstance(phy[i], basestring) and 'wlan0-ap' in phy[i]:
                try:
                    curfreq = re.search(r'(\d+) [Mm][Hh][Zz]', '\n'.join(phy[i+1])).group(1)
                except:
                    pass
                noht = re.search(r'[Nn][Oo] HT', '\n'.join(phy[i+1]))

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

if curfreq != targetfreq:
    input = subprocess.check_output('hostapd_cli chan_switch 1 ' + str(targetfreq) + (' ht' if not noht else ''), shell=True)

print '(Target frequency matched.)'

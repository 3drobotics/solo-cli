import flash
import wifi
import info
import provision
import soloutils
import logs
import install_pip
import install_smart
import install_runit
import resize
import script
import video
import pack

import sys
import paramiko
import time
import socket
import os
import tempfile
import urlparse
import urllib2

def _connect(ip, await=True, silent=False):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    socket.setdefaulttimeout(5)
    message = silent
    start = time.time()
    while True:
        try:
            client.connect(ip, username='root', password='TjSDBkAu', timeout=5)
        except paramiko.BadHostKeyException:
            print 'error: {} has an incorrect entry in ~/.ssh/known_hosts. please run:'.format(ip)
            print ''
            print '    ssh-keygen -R {}'.format(ip)
            print ''
            print 'and try again'
            sys.exit(1)
        except Exception as e:
            if not await:
                raise e
            if not message and time.time() - start > 5:
                message = True
                print '(note: ensure you are connected to Solo\'s wifi network.)'
            client.close()
            continue
        time.sleep(1)
        break
    socket.setdefaulttimeout(None)

    return client

def connect_controller(await=True, silent=False):
    return _connect('10.1.1.1', await=await, silent=silent)

def connect_solo(await=True, silent=False):
    return _connect('10.1.1.10', await=await, silent=silent)

def command_stream(client, cmd, stdout=sys.stdout, stderr=sys.stderr):
    chan = client.get_transport().open_session()
    chan.exec_command(cmd)
    while True:
        time.sleep(0.1)
        if chan.recv_ready():
            str = chan.recv(4096).decode('ascii')
            if stdout:
                stdout.write(str)
        if chan.recv_stderr_ready():
            str = chan.recv_stderr(4096).decode('ascii')
            if stderr:
                stderr.write(str)
        if chan.exit_status_ready():
            break
    code = chan.recv_exit_status()
    chan.close()
    return code

def command_blind(client, cmd):
    chan = client.get_transport().open_session()
    chan.exec_command(cmd)

def command(client, cmd):
    chan = client.get_transport().open_session()
    chan.exec_command(cmd)
    stderr = ''
    stdout = ''
    while True:
        time.sleep(0.1)
        if chan.recv_ready():
            stdout += chan.recv(4096).decode('ascii')
        if chan.recv_stderr_ready():
            stderr += chan.recv_stderr(4096).decode('ascii')
        if chan.exit_status_ready():
            break
    code = chan.recv_exit_status()
    chan.close()
    return code, stdout, stderr

def controller_versions(controller):
    code, controller_str, stderr = soloutils.command(controller, 'cat /VERSION')
    version, ref = controller_str.strip().split()
    return {
        "version": version,
        "ref": ref,
    }

def solo_versions(solo):
    code, solo_str, stderr = soloutils.command(solo, 'cat /VERSION')
    version, ref = solo_str.strip().split()
    return {
        "version": version,
        "ref": ref,
    }

def gimbal_versions(solo):
    code, gimbal_str, stderr = soloutils.command(solo, 'cat /AXON_VERSION')
    try:
        version, = gimbal_str.strip().split()
        return {
            "version": version,
            "connected": True,
        }
    except:
        return {
            "connected": False,
        }

def pixhawk_versions(solo):
    code, pixhawk_str, stderr = soloutils.command(solo, 'cat /PIX_VERSION')
    version, apm_ref, px4firmware_ref, px4nuttx_ref = pixhawk_str.strip().split()
    return {
        "version": version,
        "apm_ref": apm_ref,
        "px4firmware_ref": px4firmware_ref,
        "px4nuttx_ref": px4nuttx_ref,
    }

def settings_reset(target):
    code = soloutils.command_stream(target, 'sololink_config --settings-reset')
    if code != 0:
        code = soloutils.command_stream(target, 'mkdir -p /log/updates && touch /log/updates/RESETSETTINGS && shutdown -r now')
    return code == 0

def factory_reset(target):
    code = soloutils.command_stream(target, 'sololink_config --factory-reset')
    if code != 0:
        code = soloutils.command_stream(target, 'mkdir -p /log/updates && touch /log/updates/FACTORYRESET && shutdown -r now')
    return code == 0

def await_net():
    socket.setdefaulttimeout(5)
    while True:
        try:
            socket.gethostbyname('example.com')
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            time.sleep(0.1)
            continue

        try:
            request = urllib2.Request('http://example.com/')
            urllib2.urlopen(request)
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            time.sleep(0.1)
            continue
        else:
            break

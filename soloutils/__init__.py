import update
import wifi
import reset
import version
import provision
import soloutils
import logs

import sys
import paramiko
import time
import socket

def _connect(ip, await=True):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    socket.setdefaulttimeout(5)
    failcount = 0
    while True:
        try:
            client.connect(ip, username='root', password='TjSDBkAu', timeout=5)
        except Exception as e:
            if not await:
                raise e
            failcount += 1
            if failcount == 1:
                print '(note: ensure you are connected to Solo\'s wifi network.)'
            continue
        time.sleep(0.1)
        break
    socket.setdefaulttimeout(None)

    return client

def connect_controller(await=True):
    return _connect('10.1.1.1', await=await)

def connect_solo(await=True):
    return _connect('10.1.1.10', await=await)

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
    version, = gimbal_str.strip().split()
    return {
        "version": version,
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

import update
import tunnel
import reset
import info

import sys
import paramiko
import time
import socket

def _connect(ip, await=True):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    socket.setdefaulttimeout(5)
    while True:
        try:
            client.connect(ip, username='root', password='TjSDBkAu', timeout=5)
        except Exception as e:
            if not await:
                raise e
            continue
        time.sleep(0.1)
        break
    socket.setdefaulttimeout(None)

    return client

def connect_controller(await=True):
    return _connect('10.1.1.1', await=await)

def connect_solo(await=True):
    return _connect('10.1.1.10', await=await)

def command_stream(client, cmd):
    chan = client.get_transport().open_session()
    chan.exec_command(cmd)
    while True:
        time.sleep(0.1)
        if chan.recv_ready():
            sys.stdout.write(chan.recv(4096).decode('ascii'))
        if chan.recv_stderr_ready():
            sys.stderr.write(chan.recv_stderr(4096).decode('ascii'))
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

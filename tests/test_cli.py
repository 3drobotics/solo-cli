import subprocess

def test_cli():
	subprocess.check_call(['solo', '--help'])

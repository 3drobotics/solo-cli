# solo-utils

Install this on your **host** computer to access some sweet Solo development utilities.

```
pip install git+https://github.com/3drobotics/solo-utils
```

## instructions

```
$ solo
Usage:
  solo tunnel --name=<n> --password=<p>

Options:
  -h --help        Show this screen.
  --name=<n>       WiFi network name.
  --password=<p>   WiFi password.
```

### tunnel

`solo tunnel` connects your Controller to a local wifi network. First connect your PC to Solo's wifi network, then run this tool. After it's set up, you will have access to Solo and the Controller by their IPs, but also access to the Internet on your PC, Solo, and the Controller. (Note: after running this command, you may need to restart Solo to get access to the Internet.)

```
$ solo tunnel --name="my" --password="wifi network"
...
you are now connected to the internet.
setup complete.
```

## License

MIT/Apache-2.0

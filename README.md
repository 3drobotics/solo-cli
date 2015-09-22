# solo dev utilities

Install this on your **PC** to access some sweet Solo development utilities.

```
pip install git+https://github.com/3drobotics/solo-utils
```

Your **PC** will now have a `solo` command line tool allowing you to access the following tools.

## cli

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

`solo tunnel` connects your Controller to a local wifi network, allowing you to develop for Solo while also enabling connection to the outside Internet.

1. Turn on your Controller. Connect your PC to to the Controller's WiFi network.
2. Run this command from your PC's command line. Specify your local wifi network and password as the `--name` and `--password` arguments.
3. Turn on (or restart) Solo.

You will now have access to the Internet on your PC, Solo, and the Controller. You can still connect to Solo and the Controller by their dedicated IP addresses (`10.1.1.1` and `10.1.1.10`), while the Controller is also assigned its own IP on your local WiFi network.

```
$ solo tunnel --name="my" --password="wifi network"
...
you are now connected to the internet.
setup complete.
```

## License

MIT/Apache-2.0

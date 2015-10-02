# Solo CLI

*Solo CLI* is a command-line tool that you install on your **computer** to control, update, or connect with Solo for development.

```
sudo pip install -UI git+https://github.com/3drobotics/solo-cli
```

Your Computer will now have a `solo` command line tool. Read on for what commands are available.


## cli

```
$ solo
Solo command line utilities.

Usage:
  solo info
  solo wifi --name=<n> --password=<p>
  solo update (solo|controller|both) (latest|<version>)
  solo revert (solo|controller|both) (latest|current|factory|<version>)
  solo provision
  solo resize
  solo logs (download)
  solo install-pip
  solo install-smart
  solo install-runit
  solo video (acquire|restore)

Options:
  -h --help        Show this screen.
  --name=<n>       WiFi network name.
  --password=<p>   WiFi password.
```


### wifi

`solo wifi` connects your Controller to a local wifi network, allowing you to develop for Solo while also enabling connection to the outside Internet.

1. Turn on your Controller. Connect your PC to to the Controller's WiFi network.
2. Run this command from your PC's command line. Specify your local wifi network and password as the `--name` and `--password` arguments.
3. Turn on (or restart) Solo.

You will now have access to the Internet on your PC, Solo, and the Controller. You can still connect to Solo and the Controller by their dedicated IP addresses (`10.1.1.1` and `10.1.1.10`), while the Controller is also assigned its own IP on your local WiFi network.

```
$ solo wifi --name="wifi ssid" --password="wifi password"
...
you are now connected to the internet.
setup complete.
```


### update and revert

`solo update` will update Solo to a given version. This process does not clear user modifications to the filesystem, so ensure that the update process will not be impacted by these.

`solo revert` destructively reverts Solo to a given version, including to factory ("gold") settings. This removes all user modifications from the filesystem, and is recommended if you do not care about losing these changes.


### resize

`solo resize` resizes Solo's user partition to about ~500mb, shrinking the `/log` partition.

**TODO:** A bug exists that requires you to run this twice, i.e. once more after Solo resets the first time.


### install-pip, install-runit, install-smart

These install `pip`, the Python package manager, `runit`, a startup service manager, and `smart`, the package manager for Solo and its repository locations.

**NOTE:** In the future these might be merged into a "dev upgrade" command.


### info

`solo info` dumps to the command line the versions of all components of Solo and the Controller.


### provision

`solo provision` copies your SSH key to Solo so you can SSH in without being prompted for a password.


### logs

Download logs from Solo into your current folder.


### video

* `acquire` frees `/dev/video0` for scripts to use it as a video source.
* `restore` restores the video downlink to apps, reclaiming `/dev/video0`.


## License

MIT/Apache-2.0

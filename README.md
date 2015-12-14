# Solo CLI

*Solo CLI* is a command-line tool that you install on your computer to control, update, or connect with Solo for development.

If you installed an old version of solo-cli, first run:

```
sudo pip uninstall soloutils || true
```

To install solo-cli, run:

```
sudo pip uninstall solo-cli || true
sudo pip install https://github.com/3drobotics/solo-cli/archive/master.zip --no-cache-dir
```

Your Computer will now have a `solo` command line tool. Read on for what commands are available.


## cli

```
$ solo
Solo command line utilities.

Usage:
  solo info
  solo wifi --name=<n> [--password=<p>]
  solo flash (drone|controller|both) (latest|current|factory|<version>) [--clean]
  solo flash --list
  solo flash pixhawk <filename>
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
  --list           Lists available updates.
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


### flash

`solo flash` will update Solo and the Controller to a given version.

* `latest` refers to the most recent stable released firmware.
* `current` refers to what is currently installed. (Useful for clearing user settings via `--clean`)
* `factory` refers to the "golden" factory image originally shipped with Solo.

You can specify the `--clean` parameter to clear all user modifications to the filesystem. By omitting this flag, the update will proceed as best as it can, though some user modifications can potentially interfere with newer updates. It's recommended you back up any files you don't want destroyed.


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


### script

Runs a script on Solo.

Create a folder containing your Python code and all dependencies listed in a "requirements.txt" file. `cd` into the directory. With an Internet connection, run:

```
solo script pack
```

This will create a file "solo-script.tar.gz" which will be deployed to Solo. Next, connect to Solo's wifi and run:

```
solo script run main.py
```

Where "main.py" is the name of the file you want to use.

Look at the "script-example/" directory in this repo for an example.


### video

* `acquire` frees `/dev/video0` for scripts to use it as a video source.
* `restore` restores the video downlink to apps, reclaiming `/dev/video0`.


## License

MIT/Apache-2.0

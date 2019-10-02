# Synoindex Watcher - Automated media index updates

Synoindex Watcher is a media index updater for Synology DiskStations based on inotify and synoindex. It watches the
media-folders of your DiskStation an updates the media index every time a file or directory inside the media-folders is
created, deleted or changed. It is written in Python and licensed as open-source under the GPL version 3.

The original version was written by Mark Houghton, who [published it in his "codesourcery"
blog](https://codesourcery.wordpress.com/2012/11/29/more-on-the-synology-nas-automatically-indexing-new-files/).

## Features

* **Lightweight** No need to install extra Synology packages
* **Intelligent** Executes only if a file has actually been added/deleted/renamed
* **Agnostic** Python 2 and Python 3 compatible (minimum tested version is 2.7)

## Installation

Synoindex Watcher cannot be installed via Synology's Package Center. You have to log in via SSH and use the terminal.
I recommend to use pip for the installation. Synology DiskStations do not have pip installed by default, but you can
add it easily with the following command:

```
$ sudo python -m ensurepip
```

Now you can install the synoindexwatcher module:

```
$ sudo python -m pip install https://github.com/letorbi/synoindexwatcher/archive/master.zip
```

This will also install its dependency [inotifyrecursive](https://pypi.org/project/inotifyrecursive/).

## Usage

You can start Synoindex Watcher with the following command:

```
$ python -m synoindexwatcher
```

Add `-h` or `--help` to see the list of available parameters:

```
$ python -m synoindexwatcher --help
```

### Start on boot

Synoindex Watcher can also be run as a daemon. Use the following commands to create an init-script that starts
Synoindex Watcher in the background when your DiskStation boots:

```
$ python -m synoindexwatcher --generate-init | sudo tee /usr/local/etc/rc.d/S99synoindexwatcher.sh
$ sudo chmod a+x /usr/local/etc/rc.d/S99synoindexwatcher.sh
```

You can also use the saved init-script to stop and start the Synoindex Watcher daemon:

```
$ sudo /usr/local/etc/rc.d/S99synoindexwatcher.sh stop
$ sudo /usr/local/etc/rc.d/S99synoindexwatcher.sh start
```

----

Copyright 2019 Torben Haase \<[https://pixelsvsbytes.com](https://pixelsvsbytes.com)>

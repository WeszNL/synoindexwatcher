#
#  This file is part of Synoindex Watcher.
#
#  Copyright (c) 2012-2018 Mark Houghton <https://codesourcery.wordpress.com>
#  Copyright (c) 2019 Torben Haase <https://pixelsvsbytes.com>
#
#  Synoindex Watcher is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Synoindex Watcher is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
#  details. You should have received a copy of the GNU General Public License
#  along with Synoindex Watcher. If not, see <https://www.gnu.org/licenses/>.
#
################################################################################

import sys
import os
import subprocess
import signal
import argparse
import logging
import time
import configparser

from inotifyrecursive import INotify, flags

import files
import init

def process_create(filepath, is_dir):
    arg = ""
    if is_dir:
        arg = "-A"
    else:
        arg = "-a"
    do_index_command(filepath, is_dir, arg)

def process_delete(filepath, is_dir):
    arg = ""
    if is_dir:
        arg = "-D"
    else:
        arg = "-d"
    do_index_command(filepath, is_dir, arg)

def process_modify(filepath, is_dir):
    do_index_command(filepath, is_dir, "-a")

def do_index_command(filepath, is_dir, index_argument):
    logging.info("synoindex %s %s" % (index_argument, filepath))
    subprocess.call(["synoindex", index_argument, filepath])

def is_allowed_path(name, parent, is_dir):
    # Don't watch hidden files and folders
    if name[:1] == b'.':
        return False
    # Don't watch special files and folders
    if name[:1] == b'@':
        return False
    # Don't check the extension for directories
    if not is_dir:
        ext = os.path.splitext(name)[1][1:].lower()
        if ext in excluded_exts:
            return False
    return True

def start():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='*',
        help="add a path that shall be watched")
    parser.add_argument("--config", default=None,
        help="use a config-file")
    parser.add_argument("--logfile", default=False,
        help="set the log-file for program messages")
    parser.add_argument("--loglevel", default=False,
        help="set the minimum level that shall be logged")
    parser.add_argument("--generate-config", action="store_const", const=True,
        default=False, help="generate and print a config-file")
    parser.add_argument("--generate-init", action="store_const", const=True,
        default=False, help="generate and print an init-script")
    parser.add_argument("--pidfile", default="/var/run/synoindexwatcher.pid",
        help="set the pid-file used in the init-script")
    args = parser.parse_args()

    if args.generate_init:
        print(init.generate(args.pidfile, args.logfile, args.loglevel))
        exit(0)

    if args.generate_config:
        print(files.generateConfig(args))
        exit(0)

    config = configparser.ConfigParser(allow_no_value=True)
    if args.config != None:
        config.read(args.config)

    logfile = args.logfile if args.logfile\
        else config.get("DEFAULT", "logfile", fallback=None)
    loglevel = args.loglevel if args.loglevel\
        else config.get("DEFAULT", "loglevel", fallback="INFO")
    logging.basicConfig(filename=logfile, level=loglevel.upper(),
        format="%(asctime)s %(levelname)s %(message)s")

    signal.signal(signal.SIGTERM, sigterm)

    inotify = INotify()
    mask = flags.DELETE | flags.CREATE | flags.MOVED_TO | flags.MOVED_FROM | flags.MODIFY
    paths = args.path if len(args.path) else config.sections()
    if not len(paths):
        parser.print_help()
        exit(1)
    for path in paths:
        logging.info("Adding watch for path: %s", path)
        inotify.add_watch_recursive(path.encode('utf-8'), mask, is_allowed_path)

    logging.info("Waiting for media file changes...")
    try:
        while True:
            for event in inotify.read():
                is_dir = event.mask & flags.ISDIR
                path = os.path.join(inotify.get_path(event.wd).decode('utf-8'), event.name)
                if event.mask & flags.CREATE or event.mask & flags.MOVED_TO:
                    process_create(path, is_dir)
                elif event.mask & flags.DELETE or event.mask & flags.MOVED_FROM:
                    process_delete(path, is_dir)
                elif event.mask & flags.MODIFY:
                    process_modify(path, is_dir)
    except KeyboardInterrupt:
        logging.info("Watching interrupted by user (CTRL+C)")

def sigterm(signal, frame):
    logging.info("Process received SIGTERM signal")
    sys.exit(0)

# TODO The original script only allowed certain extensions.
#      Maybe we should have a whilelist and a blacklist.
excluded_exts = ["tmp"]

if __name__ == "__main__":
    try:
        start()
    except Exception:
        logging.exception("An uncaught exception occurred")
        sys.exit(255)

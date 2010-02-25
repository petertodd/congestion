# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

__version__ = "0.0"

import sys

from Congestion.network import world
from Congestion.ui import UserInterface

def main(argv):
    """
    Script entry point.

    Parse the command line options.
    """
    global __version__

    from optparse import OptionParser

    parser = OptionParser(usage="usage: %prog [OPTION...] command [ARG...]",version=__version__)

    parser.set_defaults(message="Hello World!")

    parser.add_option("--message","-m",
            action="store", type="string", dest="message",
            help="set message to display, defaults to %default")

    (options, args) = parser.parse_args(argv)

    ui = UserInterface(world,(1024,768))

    dt = 0.02
    import time
    last = time.time()
    while True:
        world.do(dt)
        ui.do(dt)
        
        now = time.time()
        sleep_for = dt-(now-last)
        if sleep_for > 0:
            time.sleep(sleep_for)
        last = now

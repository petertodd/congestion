# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Trains - train network thingy
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

__version__ = "0.0"

import sys

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


    import ui
    from Trains.Simulator.network import *

    net = Network(sys.stdin)

    net.add_random_trains()

    ui = ui.UserInterface(net,(1024,768))


    dt = 0.02
    while True:
        net.do(dt)
        ui.do()
        
        import time
        time.sleep(dt)

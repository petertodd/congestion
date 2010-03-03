# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

__version__ = "0.0"

import sys

from Congestion.world import world,RoundaboutIntersection
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

    #a = world.add_intersection((200,100))
    #a = world.add_intersection((200,100))
    #b = world.add_intersection((100,200))

    a = world.add_intersection((100,100),RoundaboutIntersection)
    b = world.add_intersection((200,150),RoundaboutIntersection)
    c = world.add_intersection((150,200),RoundaboutIntersection)

    d = world.add_intersection((125,300),RoundaboutIntersection)
    e = world.add_intersection((175,300),RoundaboutIntersection)

    world.connect_intersections(b,c)
    world.connect_intersections(a,b)
    world.connect_intersections(c,a)
    world.connect_intersections(c,d)
    world.connect_intersections(c,e)
    world.connect_intersections(e,d)
    world.build()

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

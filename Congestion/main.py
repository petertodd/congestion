# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

__version__ = "0.0"

import sys
import random

from Congestion.world import world,RoundaboutIntersection
from Congestion.train import Train
from Congestion.ui import run_ui

import numpy as np
from scipy.spatial import distance_matrix,KDTree

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

    width = 1920
    height = 1080
    border = 30
    min_dist = 10
    num_nodes = 500

    # Load road list
    inters = {}
    conns = {}
    fpath = open('path_gen.paths','r')
    for l in fpath.readlines():
        a1,a2,b1,b2 = [float(i) * 1000 for i in l.split(' ')]

        a = None
        if (a1,a2) not in inters:
            inters[(a1,a2)] = a = world.add_intersection((a1,a2),RoundaboutIntersection)
        else:
            a = inters[(a1,a2)]

        b = None
        if (b1,b2) not in inters:
            inters[(b1,b2)] = b = world.add_intersection((b1,b2),RoundaboutIntersection)
        else:
            b = inters[(b1,b2)]

        if (a,b) not in conns and (b,a) not in conns:
            conns[(a,b)] = True
            world.connect_intersections(a,b)

    world.build()

    dens = 0
    if True:
        all_rails = []
        for track in world.tracks:
            for rail in track.left_rails + track.right_rails:
                all_rails.append(rail)
        for rail in all_rails[::1]:
            dens += 1
            if 0 == dens % 20:
                rail.add_train(Train(rail),0)
    else:
        world.tracks[0].left_rails[0].add_train(Train(world.tracks[0].left_rails[0]),0)
        world.tracks[1].left_rails[0].add_train(Train(world.tracks[1].left_rails[0]),0)

    run_ui(world,0.05)

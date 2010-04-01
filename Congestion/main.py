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
    min_dist = 25
    num_nodes = 100

    # Build up n random nodes, such that no node is closer to any other node than min_dist
    #   
    # Naive algorithm, add nodes one at a time, and test 
    nodes = []
    while len(nodes) < num_nodes:
        nodes.append((((width - 2*border) * random.random()) + border,
                      ((height - 2*border) * random.random()) + border))
        dists = distance_matrix(nodes,nodes)

        # Remove the 0's down the diag
        dists += np.eye(len(nodes),len(nodes)) * min_dist

        if dists.min() < min_dist:
            nodes.pop()

    # Now generate a graph by going through each node, and finding the closest
    # nodes to it.
    kdt = KDTree(nodes)
    conns = {}
    for n in nodes:
        conns[n] = set()
    for n in nodes:
        dists,idxs = kdt.query(n,k=random.randrange(3,5))

        dists = dists[1:num_nodes] # throw away the 'match' to node n
        idxs = idxs[1:num_nodes]

        for d,i in zip(dists,idxs):
            conns[n].add(nodes[i])
            conns[nodes[i]].add(n)
    

    inters = {}
    for n in nodes:
        i = world.add_intersection(n,RoundaboutIntersection)
        inters[n] = i

    # Turn the connection list into roads. Each connection creates a single
    # road, from k to v
    pairs_done = {}
    for k,v in conns.iteritems():
        for r in v:
            if (k,r) not in pairs_done and (r,k) not in pairs_done:
                pairs_done[(k,r)] = True
                world.connect_intersections(inters[k],inters[r])

    world.build()

    if True:
        all_rails = []
        for track in world.tracks:
            for rail in track.left_rails + track.right_rails:
                all_rails.append(rail)
        for rail in all_rails[::1]:
            rail.add_train(Train(rail),0)
    else:
        world.tracks[0].left_rails[0].add_train(Train(world.tracks[0].left_rails[0]),0)
        world.tracks[1].left_rails[0].add_train(Train(world.tracks[1].left_rails[0]),0)

    run_ui(world,0.05)

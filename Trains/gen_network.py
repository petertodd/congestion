# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# ### BOILERPLATE ###
# Trains - train network thingy
# Copyright (C) 2007 Peter Todd <pete@petertodd.org>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ### BOILERPLATE ###

"""Ways of generating random networks from scratch."""

from random import random,randrange
from network import *
from sets import Set
from intersect import Intersect 

def find_not_fully_reachable(net):
    """Returns list of what nodes are not reachable by other nodes.
       
       
        A node is defined as always being able to reach itself.   
    """

    # Fairly simple algorithm. We maintain a set of reachable nodes for for
    # each node in the system. Then for each node, we do a search finding
    # everything that is connected. The optimization lies in that once we
    # know what nodes are reachable from a given node, if a search
    # encounters that node, we can simply take that list of nodes rather
    # than perform the search again.

    # Create empty "can reach" table
    reaches = {}
    for a in net.nodes:
        reaches[a] = Set()

    r = []
    all_nodes = Set(net.nodes)
    for n in net.nodes:
        reaches[n].add(n) # we can reach ourselves

        # Breadth first search of all connected nodes.
        l = [t.b for t in n.exits]
        for i in l:
            # Already know we can reach this node?
            if not (i in reaches[n]):
                # Reachability already calculated?
                if reaches[i]:
                    # Yes, just add the sets of reachable nodes together.
                    reaches[n] |= reaches[i]
                else:
                    # Mark that we can reach i and add it's exits the list of
                    # nodes to consider. 
                    reaches[n].add(i)
                    l += [t.b for t in i.exits]
        j = all_nodes - reaches[n]
        if j:
            r.append((n,j))

    return r

def add_track_to_closest_node(net,a,nodes):
    """Given node a finds the closest node from nodes and adds a track between them.
       
       If the closest would result in two tracks intersecting, tries the next
       best and so on.

       Returns true if this was possible to do.
    """

    dists = []
    for b in nodes:
        d = min([abs(a.pos[0] - b.pos[0]),abs(a.pos[1] - b.pos[1])])
        dists.append((d,b))

    dists = sorted(dists)

    # Try each possibility, closest first.
    for d,b in dists:
        # Don't try to create tracks to ourselves
        if a == b:
            continue 

        # Is there already a track between the two in either direction?
        if a.is_exit(b) or b.is_exit(a):
            continue

        if not net.add_track(a,b):
            return True

    return False

def gen_random_network(net,n = 10,edge_buffer = 10):
    """Create a random network.
       
       n - number of tracks to add
    """

    # add a bunch of random nodes to start with
    for i in range(0,n):
        net.nodes.append(
                Node(
                     (
                      (random() * (net.width - (edge_buffer * 2))) + edge_buffer,
                      (random() * (net.height - (edge_buffer * 2)) + edge_buffer)
                     )
                    )
                )

    while True:
        not_reachable = find_not_fully_reachable(net)
        if not not_reachable:
            break

        for a,n in not_reachable:
            add_track_to_closest_node(net,a,n)

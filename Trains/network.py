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

from random import random,randrange

from train import Train

class Node:
    """A single node within the train network."""

    # The physical position of the node
    pos = (0,0)

    # The list of tracks going from this node
    exits = False 

    # The trains occupying this node
    present = False

    def __init__(self,pos):
        self.pos = pos
        self.exits = []
        self.present = []

class Track:
    """A single track within the train network.
       
       Tracks are one way, a to b.
       """

    # The end points
    a = False
    b = False

    # Length, pre-calculated
    length = False

    # The trains occupying this track 
    present = False 

    def __init__(self,a,b):
        self.a = a
        self.a.exits.append(self)
        self.b = b

        from math import sqrt

        dx = b.pos[0] - a.pos[0]
        dy = b.pos[1] - a.pos[1]
        self.length = sqrt((dx ** 2) + (dy ** 2))

        self.present = []

class Network:
    """The graph of the train network."""

    # All the nodes and tracks in the system
    nodes = False
    tracks = False

    # Width and height of the playfield
    width = False
    height = False

    # Trains present in the system
    trains = False

    def __init__(self,dims):
        self.width,self.height = dims

        self.nodes = []
        self.tracks = []
        self.trains = []

    def do(self,delta_t):
        for t in self.trains:
            t.do(delta_t)

    def add_random_tracks(self,n = 20):
        """Add random tracks to the network.
           
           n - number of tracks to add
        """

        # add a bunch of random nodes to start with
        for i in range(0,n * 2):
            self.nodes += [Node((random() * self.width,random() * self.height))]

        # now for each node, interconnect it with some random other node to create
        # a track
        for a in self.nodes:
            while True:
                print "from the top"
                b = self.nodes[randrange(0,len(self.nodes))]

                # check for intersections with all current tracks
                from intersect import Intersect 

                for t in self.tracks:
                    if (Intersect((a.pos,b.pos),(t.a.pos,t.b.pos))):
                        print "intersects"
                        break
                else:
                    break

            self.tracks.append(Track(a,b))

    def add_random_trains(self,n = 4):
        """Add random trains to the network."""

        for i in range(0,n):
            t = self.tracks[randrange(0,len(self.tracks))]
            self.trains.append(Train(t))

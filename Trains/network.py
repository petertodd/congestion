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
from intersect import Intersect
from train import Train
from sets import Set

class Node:
    """A single node within the train network."""

    # The physical position of the node
    pos = (0,0)

    # The list of tracks going from this node
    exits = False 

    def __init__(self,pos):
        x,y = pos
        self.pos = (int(x),int(y))
        self.exits = []

    def is_exit(self,b):
        """Returns true if node b is an exit."""
        x = Set()
        for y in self.exits:
            x.add(y.b)
        return b in x

    def __str__(self):
        return str(self.pos)

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

    # Reported traffic
    traffic = False

    def __init__(self,a,b):
        self.a = a
        self.a.exits.append(self)
        self.b = b

        from math import sqrt

        dx = b.pos[0] - a.pos[0]
        dy = b.pos[1] - a.pos[1]
        self.length = int(sqrt((dx ** 2) + (dy ** 2)))

        self.present = []
        self.traffic = 0

    def maintain(self,delta_t):
        """Maintain the track, statistics and the like."""

        # Traffic reports get out of date if no-one is using the track.
        if not self.present:
            self.traffic = max(self.traffic - (self.length * delta_t),0)

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
        for t in self.tracks:
            t.maintain(delta_t)

    def add_track(self,a,b):
        """Add a track between a and b.

           If the new track would intersect other existing tracks, returns the
           list of such tracks. Otherwise returns None and succeeds.
        """

        r = []
        for t in self.tracks:
            if Intersect((a.pos,b.pos),(t.a.pos,t.b.pos)):
                r.append(t)
        if not r:
            self.tracks.append(Track(a,b))
        return r

    def add_random_trains(self,n = 20):
        """Add random trains to the network."""

        for i in range(0,n):
            t = self.tracks[randrange(0,len(self.tracks))]
            self.trains.append(Train(self,t))

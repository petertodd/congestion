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

import Trains.network

from random import random,randrange
from train import Train
from sets import Set

class Node(Trains.network.Node):
    """A single node within the train network."""

    def __init__(self,pos):
        Trains.network.Node.__init__(self,pos)

class Track(Trains.network.Track):
    """A single track within the train network.
       
       Tracks are one way, a to b.
       """

    # The trains occupying this track 
    present = False 

    # Trains waiting to enter this track.
    waiting_to_enter = None

    # Reported traffic
    traffic = False

    def __init__(self,a,b):
        Trains.network.Track.__init__(self,a,b)

        self.present = []
        self.waiting_to_enter = []
        self.traffic = 0

    def maintain(self,delta_t):
        """Maintain the track, statistics and the like."""

        # If no-one is waiting to enter, there isn't any traffic... 
        if not self.waiting_to_enter:
            self.traffic = 0  

class Network(Trains.network.Network):
    """The graph of the train network."""

    # Trains present in the system
    trains = [] 

    node_generator = Node
    track_generator = Track

    def __init__(self,f = None):
        """Create a new Network

        f - Optional file handle to load network from"""

        Trains.network.Network.__init__(self,f)

        self.trains = []

    def do(self,delta_t):
        for t in self.trains:
            t.do(delta_t)
        for t in self.tracks:
            t.maintain(delta_t)

    def add_random_trains(self,n = 20):
        """Add random trains to the network."""

        for i in range(0,n):
            t = self.tracks[randrange(0,len(self.tracks))]
            self.trains.append(Train(self,t))

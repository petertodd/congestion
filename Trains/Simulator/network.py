# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

import random
from collections import deque

import Trains.network

from train import Train
from sets import Set

class Node(Trains.network.Node):
    """A single node connecting tracks.

    Only one Train may occupy a node at any one time. Nod
    """

    occupying = False # The train occupying this Node, may be None

    def __init__(self,pos):
        Trains.network.Node.__init__(self,pos)

class Track(Trains.network.Track):
    """A single track within the train network.
       
       Tracks are one way, a to b.
       """

    # The trains occupying this track 
    #
    # Implemented as a deque of [pos,train]'s, note that pos may be negative
    trains = False

    def __init__(self,a,b):
        Trains.network.Track.__init__(self,a,b)

        self.trains = deque()

    def add_train(self,train,end_pos):
        if len(self.trains) > 0 and self.trains[0][0] <= end_pos:
            return False
        else:
            self.trains.appendleft([end_pos - train.l - train.b,train])
            return True

    def occupied(self,x):
        """Return Train occupying track at position x

        Returns None if the track is empty
        """
        for pos,train in self.trains:
            if pos <= x <= train.occupying_length + pos:
                return train
            elif pos > x:
                return None
        return None

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

    def do(self,dt):
        for t in self.trains:
            t.do_extend_buffers(dt)
        for t in self.trains:
            t.do_move(dt)

    def add_random_trains(self,n = 20):
        """Add random trains to the network."""

        rndtracks = list(self.tracks)
        random.shuffle(rndtracks)
        for i,t in zip(range(0,n),rndtracks):
            self.trains.append(Train(self,t))

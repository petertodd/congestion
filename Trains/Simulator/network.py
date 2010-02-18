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

    occupying = None # The train occupying this Node, may be None

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

    def __init__(self,a,b,locking_token=-1):
        Trains.network.Track.__init__(self,a,b,locking_token)

        self.trains = deque()

    def __repr__(self):
        return 'Track(%r,%r)' % (self.a,self.b)

    def add_train(self,train,end_pos):
        if len(self.trains) > 0 and self.trains[0][0] <= end_pos:
            return False
        else:
            self.trains.appendleft([end_pos - train.l - train.b,train])
            return True

    def move_train(self,train,dp):
        """Move train by delta-p
        
        Returns True if the train has left the track.
        """
        for pt in self.trains:
            if pt[1] is train:
                pt[0] += dp
                if pt[0] >= self.length:
                    assert self.trains[-1][1] is train
                    self.trains.pop()
                    return True
                return False
        raise Exception('Train not on track')

    def find_train(self,train):
        """Return position of train on track, or None if train is not on track"""
        for p,t in self.trains:
            if t is train:
                return p
        return None

    def ok_to_enter(self):
        if self.locking_token >= 0:
            for t in self.locking_token_classes[self.locking_token]:
                if len(t.trains) > 0:
                    return False
        return True

    def occupied(self,x):
        """Return Train occupying track at position x

        Returns None if the track is empty
        """
        for pos,train in self.trains:
            if pos <= x <= train.l + train.b + pos:
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

    def add_random_trains(self,n = None):
        """Add random trains to the network."""
        rndtracks = list(self.tracks)
        random.shuffle(rndtracks)
        if n is None:
            n = int(len(rndtracks) / 1.50)
        for i,t in zip(range(0,n),rndtracks[0:n]):
            self.trains.append(Train(self,t))

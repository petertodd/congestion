# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

cimport numpy as np
import numpy as np
import math
from collections import deque

world = None

cdef class Network:
    """The graph of the train network."""

    # All the Intersections and Tracks in the system 
    cdef public intersections
    cdef public tracks

    # Playfield width,height
    cdef public playfield_dims

    def __init__(self):
        """Create a new network"""
        self.intersections = []
        self.tracks = []

    def build(self):
        for i in self.intersections:
            i.build()

    def do(self,dt):
        all_trains = []
        for track in self.tracks:
            for rail in track.left_rails + track.right_rails:
                for p,train in rail.trains:
                    all_trains.append(train)
        for intersection in self.intersections:
            for rail in intersection.rails:
                for p,train in rail.trains:
                    all_trains.append(train)

        for train in all_trains:
            train.do_plan(dt)
        for train in all_trains:
            train.do_move(dt)

    def add_intersection(self,pos,type):
        """Add an intersection to the network at pos

        Returns the added intersection
        """
        i = type(pos)
        self.intersections.append(i)
        return i

    def connect_intersections(self,a,b,**kwargs):
        """Connect intersections a and b with a track"""
        t = Track(a,b,**kwargs)
        self.tracks.append(t)
        a.add_track(t)
        b.add_track(t.reversed)
        return t

# To avoid having to have every None, Rail, Track and Intersection have points
# to the Network it is a part of, define a singular Network used by everything.
world = Network() 

cdef class Node:
    """A Node connects Rails."""

    # The physical position of the node, m's
    cdef public pos

    # Rails going from this node
    cdef public exits

    # The train occupying this node
    cdef public occupying

    def __init__(self,pos):
        self.exits = set()
        self.occupying = None
        self.pos = np.array(pos,dtype=np.float64)

    def __repr__(self):
        return '%s((%.1f,%.1f))' % (self.__class__.__name__,self.pos[0],self.pos[1])

cdef class Rail:
    """A single rail within the train network.
       
       Rails are one way, a to b.
    """

    # The end nodes 
    cdef Node _a
    property a:
        def __get__(self):
            return self._a
        def __set__(self,v):
            self._a = v
            if self._a is not None:
                self._a.exits.add(self)
                self.__recalc_length()
    cdef Node _b
    property b:
        def __get__(self):
            return self._b
        def __set__(self,v):
            self._b = v
            self.__recalc_length()

    cdef public float length

    cdef public float speed_limit

    # The trains occupying this rail
    #
    # Implemented as a deque of [pos,train]'s
    cdef public trains

    def __init__(self,Node a,Node b):
        self.length = -1
        self.a = a
        self.b = b
        self.trains = deque()
        self.speed_limit = 25.0

    cdef __recalc_length(self):
        if self.b is not None and self.a is not None:
            ba = self.b.pos - self.a.pos
            self.length = np.sqrt(np.dot(ba,ba))

    def __repr__(self):
        return '%s(%r,%r)' % (self.__class__.__name__,self.a,self.b)

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
        return True

    def occupying(self,start,end,filter):
        """Return first Train occupying track between start and end

        Returns (pos,train) where pos is the trains starting position. This may
        be negative.

        Returns None if no such train is found.
        """
        for pos,train in self.trains:
            # Don't filter hits for the train proper, we're probably running up
            # on ourselves from behind
            if pos <= start <= pos + train.l or pos <= end <= pos + train.l:
                return (pos,train)
            # Filtering hits for the buffer region is ok however, as that's
            # probably just an artifact
            elif train is not filter and \
                    (pos <= start <= pos + train.l + train.b or \
                     pos <= end <= pos + train.l + train.b):
                return (pos,train)
        return None

cdef class Intersection:
    # Center of the intersection
    cdef public pos

    cdef public list tracks
    cdef public list rails

    def __init__(self,pos):
        self.pos = np.array(pos,dtype=np.float64)
        self.tracks = []
        self.rails = []

    def add_track(self,t):
        self.tracks.append(t)

    def __repr__(self):
        return '%s((%.1f,%.1f))' % (self.__class__.__name__,self.pos[0],self.pos[1])

cdef class TrackData:
    cdef float lane_spacing
    cdef int num_lanes

cdef class Track:
    # Tracks are collections of one directional rails

    # The end intersections
    cdef public Intersection a
    cdef public Intersection b

    property lane_spacing:
        def __get__(self):
            return self._data.lane_spacing

    property num_lanes:
        def __get__(self):
            return self._data.num_lanes

    cdef TrackData _data
    cdef public Track reversed

    # Rails comprising the track
    #
    # right_rails are the rails going from a to b
    # left_rails are the rails going from b to a
    cdef public list right_rails
    cdef public list left_rails

    def __init__(self,
            Intersection a not None,Intersection b not None,
            float lane_spacing = 2.0,
            int num_lanes = 2,
            right_rails = None, left_rails = None,
            TrackData _data = None):
        self.a = a
        self.b = b

        if right_rails is None and left_rails is None and _data is None:
            self.right_rails = []
            self.left_rails = []
            self._data = TrackData()

            self._data.lane_spacing = lane_spacing
            self._data.num_lanes = num_lanes

            self.reversed = Track(b,a,
                    right_rails = self.left_rails,left_rails = self.right_rails,
                    _data = self._data)
            self.reversed.reversed = self

            for i in range(num_lanes / 2):
                self.right_rails.append(Rail(None,None))
                self.left_rails.append(Rail(None,None))
        elif right_rails is not None and left_rails is not None and _data is not None:
            self.right_rails = right_rails
            self.left_rails = left_rails
            self._data = _data
        else:
            assert False

    def __repr__(self):
        return 'Track(%r,%r)' % (self.a,self.b)



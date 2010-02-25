# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

cimport numpy as np
import numpy as np

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

        a = self.add_intersection((200,100))
        b = self.add_intersection((100,200))
        c = self.add_intersection((300,200))

        self.connect_intersections(a,b)
        self.connect_intersections(b,c)
        self.connect_intersections(c,a)

    def do(self,dt):
        pass

    def add_intersection(self,pos):
        """Add an intersection to the network at pos

        Returns the added intersection
        """
        i = Intersection(pos)
        self.intersections.append(i)
        return i

    def connect_intersections(self,a,b):
        """Connect intersections a and b with a track"""
        t = Track(a,b)
        self.tracks.append(t)
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

    def __init__(self,pos):
        self.exits = set()
        self.pos = np.array(pos,dtype=np.float64)

    def __repr__(self):
        return 'Node((%r,%r))' % (self.pos[0],self.pos[1])

cdef class Rail:
    """A single rail within the train network.
       
       Rails are one way, a to b.
       """

    # The end nodes 
    cdef public Node a
    cdef public Node b

    cdef public float length

    def __init__(self,Node a not None,Node b not None):
        self.a = a
        self.b = b

        ba = self.b.pos - self.a.pos
        self.length = np.sqrt(np.dot(ba,ba))

    def __repr__(self):
        return 'Rail(%r,%r)' % (self.a,self.b)

cdef class Intersection:
    # Center of the intersection
    cdef public pos

    def __init__(self,pos):
        self.pos = np.array(pos,dtype=np.float64)

    def __repr__(self):
        return 'Intersection((%r,%r))' % (self.pos[0],self.pos[1])

cdef class Track:
    # Tracks are collections of one directional rails

    # The end intersections
    cdef public Intersection a
    cdef public Intersection b

    # Rails comprising the track
    #
    # rails[0] are the rails going from a to b
    # rails[1] are the rails going from b to a
    rails = None

    def __init__(self,Intersection a not None,Intersection b not None):
        self.a = a
        self.b = b

        # Start with no rails assigned
        rails = [[],[]]

    def __repr__(self):
        return 'Track(%r,%r)' % (self.a,self.b)



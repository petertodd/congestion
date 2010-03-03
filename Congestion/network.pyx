# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

cimport numpy as np
import numpy as np
import math

cpdef line_intersection(np.ndarray aa,np.ndarray ab,np.ndarray ba,np.ndarray bb):
    x1 = aa[0]
    x2 = ab[0]
    x3 = ba[0]
    x4 = bb[0]
    y1 = aa[1]
    y2 = ab[1]
    y3 = ba[1]
    y4 = bb[1]
    return ((((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4))/
             ((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))),
            (((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/
             ((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))))

cpdef line_ang(np.ndarray a,np.ndarray b):
    v = b - a
    return math.atan2(v[1],v[0])


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

        #a = self.add_intersection((200,100))
        #a = self.add_intersection((200,100))
        #b = self.add_intersection((100,200))

        a = self.add_intersection((100,100))
        b = self.add_intersection((200, 75))
        c = self.add_intersection(( 75,200))

        self.connect_intersections(b,c)
        self.connect_intersections(a,b)
        self.connect_intersections(c,a)

        for i in self.intersections:
            i.build()

    def do(self,dt):
        pass

    def add_intersection(self,pos,type=RoundaboutIntersection):
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

    def __init__(self,pos):
        self.exits = set()
        self.pos = np.array(pos,dtype=np.float64)

    def __repr__(self):
        return '%s((%r,%r))' % (self.__class__.__name__,self.pos[0],self.pos[1])

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
            self.__recalc_length()
    cdef Node _b
    property b:
        def __get__(self):
            return self._b
        def __set__(self,v):
            self._b = v
            self.__recalc_length()

    cdef public float length

    def __init__(self,Node a,Node b):
        self.length = -1
        self.a = a
        self.b = b

    cdef __recalc_length(self):
        if self.b is not None and self.a is not None:
            ba = self.b.pos - self.a.pos
            self.length = np.sqrt(np.dot(ba,ba))

    def __repr__(self):
        return '%s(%r,%r)' % (self.__class__.__name__,self.a,self.b)

def track_ang_key(t):
    return line_ang(t.a.pos,t.b.pos)

cdef class Intersection:
    # Center of the intersection
    cdef public pos

    cdef public list tracks

    def __init__(self,pos):
        self.pos = np.array(pos,dtype=np.float64)
        self.tracks = []

    def add_track(self,t):
        self.tracks.append(t)
        self.tracks = sorted(self.tracks,key=track_ang_key)

    def __repr__(self):
        return '%s((%r,%r))' % (self.__class__.__name__,self.pos[0],self.pos[1])

cdef class RoundaboutIntersection(Intersection):
    def build(self):
        """"""
        # We've got a list of tracks connecting to this intersection. Each
        # track has rails assigned to it, however the nodes that define where
        # the roads end are in an undefined state. What we need to do is figure
        # out where those nodes should be, and then create the rails of the
        # roundabout linking those nodes together in a circle.

        # Walk through the pairs of Tracks, ordered by angle
        print 'walking',self
        nodes_around = [] # Ordered list of nodes on the circumfrence of the roundabout
        for t1,t2 in zip(self.tracks,self.tracks[1:] + self.tracks[0:1]):
            # FIXME: only support two lane Tracks for now

            # The incoming track of t1, connects to the outgoing track of t2.
            # To find where that intersection actually occures in physical
            # space, first we have to expand the tracks, separating the two
            # rails by the lane spacing.

            # Find the vectors of each track
            t1v = t1.b.pos - t1.a.pos
            t2v = t2.b.pos - t2.a.pos

            # Using those vectors, find points offset from the beginning by the
            # lane separation. Cross products do this nicely, essentially we
            # unitize the vector, turn it into 3d, then take the cross product
            # of that vector, and a unit vector either pointing +1Z, or -1Z, to
            # get the offset in the two needed directions.
            ut1v = np.array(t1v)
            ut1v /= np.sqrt(np.dot(ut1v,ut1v))
            ut1v.resize(3)
            ut2v = np.array(t2v)
            ut2v /= np.sqrt(np.dot(ut2v,ut2v))
            ut2v.resize(3)

            off1 = np.cross(ut1v,np.array((0,0,-1))) * (t1.lane_spacing/2)
            off1.resize(2)
            off2 = np.cross(ut1v,np.array((0,0,+1))) * (t2.lane_spacing/2)
            off2.resize(2)

            # The original vectors, and the offsets, can then be taken as line
            # equations, and the intersection of that then gives us the
            # location of the node where they connect.
            i = line_intersection(t1.a.pos + off1,t1.b.pos + off1,
                                  t2.a.pos + off2,t2.b.pos + off2)

            # Now create a Node for that intersection, and set the endpoints of
            # the rails involved.
            i = Node(i)
            assert 1 == len(t1.right_rails) == len(t2.right_rails) == len(t1.left_rails) == len(t2.left_rails)
            t1.left_rails[0].b = i
            t2.right_rails[0].a = i

            nodes_around.append(i)
            

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
            float lane_spacing = 10.0,
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



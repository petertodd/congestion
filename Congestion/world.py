# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

import pygame

import numpy as np
import math

from Congestion._world import *

def line_intersection(aa,ab,ba,bb):
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

def line_ang(a,b):
    v = b - a
    return math.atan2(v[1],v[0])

class RoundaboutIntersection(Intersection):
    def build(self):
        """"""
        # We've got a list of tracks connecting to this intersection. Each
        # track has rails assigned to it, however the nodes that define where
        # the roads end are in an undefined state. What we need to do is figure
        # out where those nodes should be, and then create the rails of the
        # roundabout linking those nodes together in a circle.

        # Order Tracks by angle
        self.tracks = list(reversed(sorted(self.tracks,key=lambda t: line_ang(t.a.pos - self.pos,t.b.pos - self.pos))))

        # Walk through the pairs of Tracks, ordered by angle
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

            off1 = np.cross(ut1v,np.array((0,0,+1))) * (t1.lane_spacing/2)
            off1.resize(2)
            off2 = np.cross(ut2v,np.array((0,0,-1))) * (t2.lane_spacing/2)
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

        # Create a clockwise loop connecting the intersections
        if len(nodes_around) > 2:
            for n1,n2 in zip(nodes_around,nodes_around[1:] + nodes_around[0:1]):
                self.rails.append(Rail(n1,n2))

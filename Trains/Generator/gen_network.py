# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Trains - train network thingy
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

import sys
from time import sleep

from random import random,randrange
from network import *

import numpy as np
import math
from scipy.spatial import distance_matrix,KDTree

import pygame

def line_intersection(aa,ab,ba,bb):
    x1 = float(aa[0])
    x2 = float(ab[0])
    x3 = float(ba[0])
    x4 = float(bb[0])
    y1 = float(aa[1])
    y2 = float(ab[1])
    y3 = float(ba[1])
    y4 = float(bb[1])
    return ((((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4))/
             ((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))),
            (((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/
             ((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))))

def ip(pos):
    x,y = pos
    return (int(x),int(y))


def gen_random_network(net,
        width=1024,height=768,
        border=30,
        num_nodes=75,
        min_dist=75,
        road_width=8):
    """Create a network. 
    """

    pygame.init()
    screen = pygame.display.set_mode((1024,768))

    # Build up n random nodes, such that no node is closer to any other node than min_dist
    #
    # Naive algorithm, add nodes one at a time, and test 
    nodes = []
    while len(nodes) < num_nodes:
        nodes.append((((width - 2*border) * random()) + border,
                      ((height - 2*border) * random()) + border))
        dists = distance_matrix(nodes,nodes)

        # Remove the 0's down the diag
        dists += np.eye(len(nodes),len(nodes)) * min_dist

        if dists.min() < min_dist:
            nodes.pop()

    # Now generate a graph by going through each node, and finding the closest
    # nodes to it.
    kdt = KDTree(nodes)
    conns = {}
    for n in nodes:
        conns[n] = set()
    for n in nodes:
        dists,idxs = kdt.query(n,k=randrange(4,6))

        dists = dists[1:num_nodes] # throw away the 'match' to node n
        idxs = idxs[1:num_nodes]

        for d,i in zip(dists,idxs):
            conns[n].add(nodes[i])
            conns[nodes[i]].add(n)

    # We've got the basic set of interconnections. Now we need to create two
    # things, roads, and intersections.
    class Intersection:
        def __init__(self,pos):
            self.pos = pos
            pygame.draw.circle(screen,(0,255,0),ip(self.pos),3)
            pygame.display.flip()
            self.ins = set() 
            self.outs = set()
        def __hash__(self):
            return hash(self.pos)
        def __repr__(self):
            return 'Intersection(%r)' % ((int(self.pos[0]),int(self.pos[1])),)
        def sort_roads(self):
            """Sort the ins and outs lists clockwise"""
            def sort_roads(roads,end):
                def ang(road):
                    v = None
                    if end:
                        v = road.a.pos
                    else:
                        v = road.b.pos
                    v = np.array(v) - np.array(self.pos)
                    a = math.atan2(v[1],v[0])
                    if a < 0:
                        return -(math.pi*2 + a)
                    else:
                        return -a
                return sorted(roads,key=ang)
            l = len(self.ins)
            self.ins = sort_roads(self.ins,True)
            assert len(self.ins) == l
            l = len(self.outs)
            self.outs = sort_roads(self.outs,False)
            assert len(self.outs) == l

    class Road:
        def __init__(self,a,b):
            self.a = a
            self.b = b
            self.pa = None 
            self.pb = None
            pygame.draw.aaline(screen,(255,0,0),ip(self.a.pos),ip(self.b.pos))
            pygame.display.flip()
        def __hash__(self):
            return hash((self.a,self.b))
        def __repr__(self):
            return 'Road(%r,%r)' % (self.a,self.b)

    # Turn nodes into intersections
    inters = {}
    for n in nodes:
        i = Intersection(n)
        inters[n] = i

    # Turn the connection list into roads. Each connection creates a single
    # road, from k to v
    pairs_done = {}
    for k,v in conns.iteritems():
        for r in v:
            if (k,r) not in pairs_done and (r,k) not in pairs_done:
                pairs_done[(k,r)] = True

                # Add roads for in and out both both this intersection, and it's connection ones
                nr = Road(inters[k],inters[r])
                inters[r].ins.add(nr)
                inters[k].outs.add(nr)

                nr = Road(inters[r],inters[k])
                inters[k].ins.add(nr)
                inters[r].outs.add(nr)

    # We can now sort the in and out roads for each intersection clockwise with respect to angle.
    for i in inters.itervalues():
        i.sort_roads()

    # Now for each road, go through the in and out roads and adjust their
    # actual endpoints to separate the lanes.
    for i in inters.itervalues():
        # Note how the out-roads array is shifted by one, visually the in road,
        # should intersect directly with the subsequent (anti-clockwise)
        # out-road.
        print >>sys.stderr,zip(i.ins,i.outs[1:] + i.outs[0:1])
        for inr,outr in zip(i.ins,i.outs[1:] + i.outs[0:1]):
            # Create versions of in and out that have been made parallel, but
            # road_width/2 distant from, the centerline, and then find where
            # they intersect.

            # Note that we are not finding the interection of the line segments
            # made by the parallel roads, rather we need to find the
            # intersection of infinitely long lines, of the correct slope,
            # passing through the endpoints.

            # Shift endpoints by the road width.
            def mk_parallel_endpoints(road,dist,dir):
                a = np.array(road.a.pos)
                a.resize(3)
                b = np.array(road.b.pos)
                b.resize(3)
                u = b-a
                u = u / np.sqrt(np.dot(u,u))
                v = np.cross(u,np.array((0,0,dir)))*dist
                a += v
                b += v
                a.resize(2)
                b.resize(2)
                return (a,b) 

            inl = mk_parallel_endpoints(inr,road_width/2,-1)
            pygame.draw.aaline(screen,(0,120,0),ip(inl[0]),ip(inl[1]))
            outl = mk_parallel_endpoints(outr,road_width/2,-1)
            pygame.draw.aaline(screen,(0,0,120),ip(outl[0]),ip(outl[1]))

            intr = line_intersection(inl[0],inl[1],outl[0],outl[1])
            intr = Node((intr[0],intr[1]))
            net.nodes.append(intr)
            assert inr.pb is None
            assert outr.pa is None
            inr.pb = intr
            outr.pa = intr
            pygame.draw.circle(screen,(0,120,0),ip(inr.pb.pos),2)
            pygame.display.flip()
            #sleep(0.1)
            pygame.draw.circle(screen,(0,120,120),ip(outr.pa.pos),2)
            pygame.display.flip()
            #sleep(0.1)
            pygame.draw.aaline(screen,(0,0,0),ip(inl[0]),ip(inl[1]))
            pygame.draw.aaline(screen,(0,0,0),ip(outl[0]),ip(outl[1]))
            pygame.display.flip()

    for i in inters.itervalues():
        # Create tracks for the roads themselves
        for r in i.ins:
            a,b = net.add_track(r.pa,r.pb)
            assert a is not None
            pygame.draw.aaline(screen,(120,0,0),ip(r.pa.pos),ip(r.pb.pos))
            pygame.display.flip()
            #sleep(0.1)

        # Create the round-about-tracks connecting the circle
        if len(i.ins) > 2:
            last = i.ins[0].pb
            locking_token = randrange(1,1000000)
            for r in i.ins[1:] + i.ins[0:1]:
                a,b = net.add_track(last,r.pb,locking_token=locking_token)
                assert a is not None
                last = r.pb

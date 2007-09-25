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

from kjbuckets import kjGraph

class Node:
    """A single node within the train network."""

    # The physical position of the node
    pos = (0,0)

    # The list of tracks going from this node
    exits = []

    # The trains occupying this node
    present = []

    def __init__(self,pos):
        self.pos = pos

class Track:
    """A single track within the train network.
       
       Tracks are one way, a to b.
       """

    # The end points
    a = False
    b = False

    # The trains occupying this track 
    present = []

    def __init__(self,a,b):
        self.a = a
        self.a.exits.append(self)
        self.b = b

class Network:
    """The graph of the train network."""

    # All the nodes and tracks in the system
    nodes = []
    tracks = []

    def __init__(self):
        n1 = Node((10,10))
        n2 = Node((10,50))
        n3 = Node((50,50))
        n4 = Node((50,10))
        a = Track(n1,n2)
        b = Track(n2,n3)
        c = Track(n3,n4)
        d = Track(n4,n1)

        self.nodes = [n1,n2,n3,n4]
        self.tracks = [a,b,c,d]

        pass

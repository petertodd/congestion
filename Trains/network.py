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

# Basic definition of a train network, with loading and saving functions.

from xml.dom.minidom import parse,Document

class Node:
    """A single node within the train network."""

    # The physical position of the node
    #
    # Nodes are uniquely identified by their position.
    pos = (None,None) 

    def __init__(self,pos):
        x,y = pos
        self.pos = (int(x),int(y))

    def __str__(self):
        return str(self.pos)

class Track:
    """A single track within the train network.
       
       Tracks are one way, a to b.
       """

    # The end nodes 
    a = False
    b = False

    def __init__(self,a,b):
        self.a = a
        self.b = b

    def length(self):
        """Returns the current length of the track"""
        dx = b.pos[0] - a.pos[0]
        dy = b.pos[1] - a.pos[1]
        return int(sqrt((dx ** 2) + (dy ** 2)))


class Network:
    """The graph of the train network."""

    # All the nodes and tracks in the system
    nodes = None 
    tracks = None

    # Width and height of the playfield
    width = None 
    height = None


    def __init__(self,f = None):
        """Create a new network

        f - Optional file handle to load network from"""

        self.nodes = []
        self.tracks = []

    def add_node(self,pos):
        """Add a node to the network at position pos"""

        n = Node(pos)

        self.nodes.append(n)

    def add_track(self,a,b):
        """Add a track to the network connecting nodes a and b"""

        t = Track(a,b)

        self.tracks.append(t)

    def load(self,f):
        """Load the network from file handle f"""

        dom = parse(f)

    def save(self,f):
        """Load the network from file handle f"""

        doc = Document()

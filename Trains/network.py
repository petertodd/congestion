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
        if type(pos) == type(()):
            x,y = pos
            self.pos = (int(x),int(y))
        elif type(pos) == type(u''):
            p = pos[1:-1].split(',')
            x = int(p[0])
            y = int(p[1])

            self.pos = (x,y)

    def __str__(self):
        return str(self.pos)

    def __eq__(self,other):
        if self.pos == other.pos:
            return True
        else:
            return False

    def __ne__(self,other):
        return not self.__eq__(other)

    def dump_dom(self,doc):
        n = doc.createElement("node")

        n.setAttribute("pos",str(self))

        return n

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

    def __eq__(self,other):
        if (self.a == other.a) and (self.b == other.b):
            return True
        else:
            return False

    def __ne__(self,other):
        return not self.__eq__(other)

    def length(self):
        """Returns the current length of the track"""
        dx = b.pos[0] - a.pos[0]
        dy = b.pos[1] - a.pos[1]
        return int(sqrt((dx ** 2) + (dy ** 2)))


    def dump_dom(self,doc):
        t = doc.createElement("track")

        t.setAttribute("a",str(self.a))
        t.setAttribute("b",str(self.b))

        return t 

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

        if f:
            self.load(f)            

    def __eq__(self,other):
        for (a,b) in zip(self.nodes,other.nodes):
            if a != b:
                return False
        for (a,b) in zip(self.tracks,other.tracks):
            if a != b:
                return False
        return True

    def __ne__(self,other):
        return not self.__eq__(other)

    def add_node(self,pos):
        """Add a node to the network at position pos"""

        n = Node(pos)

        self.nodes.append(n)

        return n

    def add_track(self,a,b):
        """Add a track to the network connecting nodes a and b"""

        t = Track(a,b)

        self.tracks.append(t)

    def load(self,f):
        """Load the network from file handle f"""

        # Clear
        self.nodes = []
        self.tracks = []


        dom = parse(f)

        train_network_elements = dom.getElementsByTagName('train_network')
        assert(train_network_elements.length == 1)
        train_network_element = train_network_elements[0]

        nodes_elements = train_network_element.getElementsByTagName('nodes')
        assert(nodes_elements.length == 1)
        nodes_element = nodes_elements[0]

        node_elements = nodes_element.getElementsByTagName('node')

        for n in node_elements:
            self.nodes.append(Node(n.getAttribute('pos')))
    
        tracks_elements = train_network_element.getElementsByTagName('tracks')

    def save(self,f):
        """Save the network to file handle f"""

        doc = Document()

        net = doc.createElement("train_network")
        doc.appendChild(net)

        nodes = doc.createElement("nodes")
        net.appendChild(nodes)

        for n in self.nodes:
            nodes.appendChild(n.dump_dom(doc))

        tracks = doc.createElement("tracks")
        net.appendChild(tracks)

        for t in self.tracks:
            tracks.appendChild(t.dump_dom(doc))

        doc.writexml(f,addindent=" ",newl="\n")

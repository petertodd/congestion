# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# Trains - train network thingy
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

# Basic definition of a train network, with loading and saving functions.

from math import sqrt

from xml.dom.minidom import parse,Document

class Node:
    """A single node within the train network."""

    # The physical position of the node
    #
    # Nodes are uniquely identified by their position.
    pos = (None,None) 

    # Tracks going from this node
    exits = set() 

    def __init__(self,pos):
        self.exits = set()
        if type(pos) == type(()):
            x,y = pos
            self.pos = (int(x),int(y))
        elif type(pos) == type(u''):
            p = pos[1:-1].split(',')
            x = int(p[0])
            y = int(p[1])

            self.pos = (x,y)
        assert self.pos[0] > 0
        assert self.pos[1] > 0

    def __str__(self):
        return str(self.pos)

    def __repr__(self):
        return 'Node(%r)' % (self.pos,)

    def __eq__(self,other):
        if type(self) != type(other):
            return False

        if self.pos == other.pos:
            return True
        else:
            return False

    def __ne__(self,other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.pos)

    def is_exit(self,b):
        """Returns true if node b is an exit."""
        x = set()
        for y in self.exits:
            x.add(y.b)
        return b in x

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

    locking_token_classes = {}

    def __init__(self,a,b,locking_token=-1):
        self.a = a
        self.a.exits.add(self)
        self.b = b
        self.locking_token=locking_token

        self.locking_token_classes.setdefault(self.locking_token,[]).append(self)

        self.length = self.calc_length()

    def __eq__(self,other):
        if type(self) != type(other):
            return False

        if (self.a == other.a) and (self.b == other.b):
            return True
        else:
            return False

    def __ne__(self,other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((hash(self.a),hash(self.b)))

    def calc_length(self):
        """Returns the current length of the track"""
        dx = self.b.pos[0] - self.a.pos[0]
        dy = self.b.pos[1] - self.a.pos[1]
        return int(sqrt((dx ** 2) + (dy ** 2)))


    def dump_dom(self,doc):
        t = doc.createElement("track")

        t.setAttribute("a",str(self.a))
        t.setAttribute("b",str(self.b))
        t.setAttribute("locking_token",str(self.locking_token))

        return t 

class Network:
    """The graph of the train network."""

    # All the nodes and tracks in the system
    nodes = None 
    tracks = None

    # Width and height of the playfield
    width = None 
    height = None


    # Generator functions to create a new Node or Track, to be changed by
    # subclasses.
    node_generator = Node
    track_generator = Track

    def __init__(self,f = None):
        """Create a new network

        f - Optional file handle to load network from"""

        self.nodes = []
        self.tracks = []

        if f:
            self.load(f)            

    def __eq__(self,other):
        if len(self.nodes) != len(other.nodes):
            return False
        for (a,b) in zip(self.nodes,other.nodes):
            if a != b:
                return False

        if len(self.tracks) != len(other.tracks):
            return False
        for (a,b) in zip(self.tracks,other.tracks):
            if a != b:
                return False

        return True

    def __ne__(self,other):
        return not self.__eq__(other)

    def add_node(self,pos):
        """Add a node to the network at position pos"""

        n = self.node_generator(pos)

        self.nodes.append(n)

        return n

    def add_track(self,a,b,locking_token=-1):
        """Add a track to the network connecting nodes a and b
        
        Returns the added track
        """

        t = self.track_generator(a,b,locking_token)

        self.tracks.append(t)

        return t

    def load(self,f):
        """Load the network from file handle f"""

        # Clear
        self.nodes = []
        self.tracks = []


        dom = parse(f)

        print dom.getElementsByTagName('train_network')

        train_network_elements = dom.getElementsByTagName('train_network')
        assert(train_network_elements.length == 1)
        train_network_element = train_network_elements[0]

        nodes_elements = train_network_element.getElementsByTagName('nodes')
        assert(nodes_elements.length == 1)
        nodes_element = nodes_elements[0]

        node_elements = nodes_element.getElementsByTagName('node')

        for n in node_elements:
            self.nodes.append(self.node_generator(n.getAttribute('pos')))
   

        tracks_elements = train_network_element.getElementsByTagName('tracks')
        assert(tracks_elements.length == 1)
        tracks_element = tracks_elements[0]

        track_elements = tracks_element.getElementsByTagName('track')

        # Nodes in the xml file have textical positions, while new Track
        # elements expect actual Node objects, so create a lookup table.
        pos2node = {}
        for n in self.nodes:
            pos2node[str(n.pos)] = n

        for t in track_elements:
            a = pos2node[t.getAttribute('a')]
            b = pos2node[t.getAttribute('b')]
            locking_token = int(t.getAttribute('locking_token'))

            self.tracks.append(self.track_generator(a,b,locking_token))

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

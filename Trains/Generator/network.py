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

# Definition of a train network, for the generator functionality. This is built
# upon the basic network in the Trains module.

import Trains.network
from Trains.Generator.intersect import Intersect

class Node(Trains.network.Node):
    """A single node within the train network."""

    def __init__(self,pos):
        Trains.network.Node.__init__(self,pos)

class Track(Trains.network.Track):
    """A single track within the train network.
       
       Tracks are one way, a to b.
       """

    def __init__(self,a,b):
        Trains.network.Node.__init__(self,a,b)

class Network(Trains.network.Network):
    """The graph of the train network."""

    # All the nodes and tracks in the system
    nodes = None 
    tracks = None

    # Width and height of the playfield
    width = None 
    height = None

    def add_track(self,a,b):
        """Add a track between a and b.

           Returns (t,i)

           Where t is the added track, or None if the track would intersect
           other tracks. In the latter case the intersecting tracks are
           returned as i
        """

        i = []
        n = None
        for t in self.tracks:
            if Intersect((a.pos,b.pos),(t.a.pos,t.b.pos)):
                i.append(t)
        if not i:
            n = Trains.network.Network.add_track(self,a,b)
        return (n,tuple(i))

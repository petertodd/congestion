# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2007 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 3.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

import os
import shutil

from Trains.tests import common 

from unittest import TestCase
from Trains.network import *

class TrainsNetworkTest(TestCase):
    """Perform tests of the Trains.network module"""

    def testNodeExits(self):
        """Node exits list is kept updated"""

        a = Node((0,0))
        b = Node((1,1))
        c = Node((2,2))

        self.assert_(a.exits == set())
        self.assert_(not a.is_exit(a))
        self.assert_(not a.is_exit(b))

        self.assert_(b.exits == set())
        self.assert_(not b.is_exit(a))
        self.assert_(not b.is_exit(b))

        self.assert_(id(a.exits) != id(b.exits))

        ta = Track(a,b)

        self.assert_(a.exits == set((ta,)))
        self.assert_(a.is_exit(b))
        self.assert_(b.exits == set())
        self.assert_(not b.is_exit(a))

        tb = Track(a,c)

        self.assert_(a.exits == set((ta,tb)))
        self.assert_(a.is_exit(b))
        self.assert_(a.is_exit(c))
        self.assert_(not a.is_exit(a))

    def testNodeComparisons(self):
        """Node comparison functions"""

        a = Node((0,0))
        b = Node((1,0))
        c = b
        d = Node((0,0))

        self.assert_(a != b)
        self.assert_(not a == b)
        self.assert_(b == c)
        self.assert_(not b != c)
        self.assert_(a == d)
        self.assert_(not a != d)

        # Comparisons also have to handle comparisons against None
        self.assert_(not a == None)
        self.assert_(a != None)
        self.assert_(not None == a)
        self.assert_(None != a)

    def testNodeHashable(self):
        """Node objects are hashable"""

        a = Node((0,0))

        hash(a)

    def testTrackHashable(self):
        """Track objects are hashable"""

        a = Node((0,0))
        b = Node((1,1))

        t = Track(a,b)

        hash(t)

    def testTrackLength(self):
        """Track.length()"""

        a = Node((0,0))
        b = Node((6,0))
        c = Node((0,8))
        d = Node((6,8))

        self.assert_(Track(a,a).length() == 0)
        self.assert_(Track(a,b).length() == 6)
        self.assert_(Track(a,c).length() == 8)
        self.assert_(Track(a,d).length() == 10)

    def testNetwork(self):
        """Network() basic functionality"""

        common.load_dataset("empty")

        net = Network()

        na = net.add_node((0,0))
        nb = net.add_node((0,1))
        nc = net.add_node((1,1))
        nd = net.add_node((1,0))

        ta = net.add_track(na,nb)
        tb = net.add_track(nb,nc)
        tc = net.add_track(nc,nd)
        td = net.add_track(nd,na)

        net.save(open(common.tmpd + "/foo",'w'))

        net2 = Network(open(common.tmpd + "/foo",'r'))

        # compare
        self.assert_(net == net2)

    def testNetworkComparisons(self):
        """Network == != comparisons work"""

        # One bug was when the two were compared with zip, which meant that if
        # the second in the comparison simply had no Nodes/Tracks, the
        # comparison returned true.
        net = Network()
        net2 = Network()

        self.assert_(net == net2)
        self.assert_(not net != net2)

        a1 = net.add_node((0,0))

        self.assert_(net != net2)
        self.assert_(not net == net2)

        a2 = net2.add_node((0,0))

        self.assert_(net == net2)
        self.assert_(not net != net2)


        b1 = net.add_node((1,0))

        self.assert_(net != net2)
        self.assert_(not net == net2)

        b2 = net2.add_node((1,0))

        self.assert_(net == net2)
        self.assert_(not net != net2)


        t1 = net.add_track(a1,b1)

        self.assert_(net != net2)
        self.assert_(not net == net2)

        t2 = net2.add_track(a2,b2)
        self.assert_(net == net2)
        self.assert_(not net != net2)

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
        nb = net.add_node((1,1))
        nc = net.add_node((0,1))
        nd = net.add_node((1,0))

        ta = net.add_track(na,nb)
        tb = net.add_track(nb,nc)
        tc = net.add_track(nc,nd)
        td = net.add_track(nd,na)

        net.save(open(common.tmpd + "/foo",'w'))

        net2 = Network(open(common.tmpd + "/foo",'r'))

        # compare
        self.assert_(net == net2)

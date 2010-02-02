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
from Trains.Simulator.network import *

class TrainsSimulatorNetworkTest(TestCase):
    """Perform tests of the Trains.Simulator.network module"""

    def testNetworkAddTrack(self):
        """Simulator.Network.add_track()/add_node() results in correct subclasses"""

        net = Network()

        na = net.add_node((0,0))
        nb = net.add_node((0,1))

        t = net.add_track(na,nb)

        self.assert_(isinstance(na,Node))
        self.assert_(isinstance(t,Track))


    def testNetworkLoadUsesNodeTrackGenerators(self):
        """Simulator.Network.load() results in correct subclasses for Node and Tracks"""
        common.load_dataset('basic_networks')

        net = Network(common.tmpd + '/square')

        for n in net.nodes:
            self.assert_(isinstance(n,Node))
        for t in net.tracks:
            self.assert_(isinstance(t,Track))

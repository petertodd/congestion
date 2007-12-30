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
from Trains.Generator.network import *

class TrainsGeneratorNetworkTest(TestCase):
    """Perform tests of the Trains.Generator.network module"""

    def testNetworkAddTrack(self):
        """Generator.Network.add_track() basic functionality"""

        common.load_dataset("basic_networks")

        net = Network()

        na = net.add_node((0,0))
        nb = net.add_node((0,1))
        nc = net.add_node((1,1))
        nd = net.add_node((1,0))


        def T(a,b,x = True,y = ()):
            (t,i) = net.add_track(a,b)

            if x:
                self.assert_(t != None)
            else:
                self.assert_(t == None)

            self.assert_(y == i)

            return t

        # Surrounding square
        T(na,nb)
        T(nb,nc)
        T(nc,nd)
        T(nd,na)

        # First diagonal
        t = T(na,nc)

        # Second diagonal, will intersect with first
        T(nb,nd,False,(t,))


        # An overlapping track should intersect as well.
        T(na,nc,False,(t,))
        T(nc,na,False,(t,))

        # FIXME: Add case for lines sharing endpoints, or completely within
        # another.

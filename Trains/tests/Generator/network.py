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
    """Perform tests of the Trains.network module"""

    def testNetwork(self):
        """Netowrk() basic functionality"""

        common.load_dataset("empty")

        n = Network()

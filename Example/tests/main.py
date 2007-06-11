# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2007 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 2.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

import os
import shutil

import common

from unittest import TestCase
from Example.main import *

class MainTest(TestCase):
    """Perform tests of the main module"""

    def testMain(self):
        """main() accepts -m"""

        common.load_dataset("empty")

        main(["-m","test message"])

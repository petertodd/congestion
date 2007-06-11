# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2007 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 2.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

import common

from unittest import TestCase

class MetaTest(TestCase):
    """Perform meta testing of the test suite"""

    def testLoadDatasetInvalid(self):
        """load_dataset() with invalid dataset should fail immediately"""

        self.assertRaises(AssertionError,common.load_dataset,"invalid dataset")

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
import os

from unittest import TestCase

class MetaTest(TestCase):
    """Perform meta testing of the test suite"""

    def testLoadDatasetInvalid(self):
        """load_dataset() with invalid dataset should fail immediately"""

        self.assertRaises(AssertionError,common.load_dataset,"invalid dataset")

        # make sure the above didn't clobber further tests 
        common.load_dataset('empty')

    def testCheckDataset(self):
        """check_dataset()"""

        def check(a,b):
            common.load_dataset(a)
            return common.check_dataset(b)

        def t(a,b):
            self.assert_(check(a,b))

        def f(a,b):
            self.assert_(not check(a,b))

        t("empty","empty")
        f("empty","check_dataset_not_empty1")
        t("check_dataset_not_empty1","check_dataset_not_empty1")
        f("check_dataset_not_empty1","check_dataset_not_empty2")
        f("check_dataset_not_empty1","check_dataset_not_empty3")
        f("check_dataset_not_empty1","check_dataset_not_empty4")
        t("check_dataset_not_empty4","check_dataset_not_empty4")

    def testCheckDatasetSymlinks(self):
        """check_dataset() knows about symlinks"""

        common.load_dataset('check_dataset_not_empty_symlink')

        # Create a symlink
        os.symlink(common.tmpd + "/foo",common.tmpd + "/bar")

        self.assert_(not common.check_dataset('check_dataset_not_empty_symlink.check'))

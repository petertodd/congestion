# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2007 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 2.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

"""Some stuff common to all tests"""

import shutil
import tempfile

tmpd = ""

def clean_tmpd():
    """Sets tmpd to a unique name guaranteed to have nothing at it."""
    global tmpd
    if not tmpd:
        tmpd = tempfile.mkdtemp(prefix="example_tests_")
    shutil.rmtree(tmpd)

def load_dataset(name):
    """Copy a dataset into the temp directory."""
    from os.path import join, split
    srcpath = join(split(__file__)[0], 'data', name)

    from os.path import exists
    assert(exists(srcpath))

    global tmpd
    clean_tmpd()

    shutil.copytree(srcpath,tmpd)
#    print "Created " + tmpd + " from dataset " + name

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
import os

tmpd = ""

def dataset_path(name):
    """Given a dataset name returns the datasets path."""
    from os.path import join, split
    path = join(split(__file__)[0], 'data', name)

    assert(os.path.exists(path))

    return path

def clean_tmpd():
    """Sets tmpd to a unique name guaranteed to have nothing at it."""
    global tmpd
    if not tmpd or not os.path.exists(tmpd):
        tmpd = tempfile.mkdtemp(prefix="train_tests_")
    shutil.rmtree(tmpd)

def load_dataset(name):
    """Copy a dataset into the temp directory."""

    global tmpd
    clean_tmpd()

    shutil.copytree(dataset_path(name),tmpd)

def repr_file(path):
    """Returns a tuple fully representing a file."""

    
    symlink = None
    try:
        symlink = os.readlink(path)
    except OSError:
        pass

    return (path,open(path).read(),symlink)

def repr_dirtree(path):
    """Return a set completely representing a directory tree."""

    # Filecmp.dircmp would be nice to use, but it doesn't seem to be recursive,
    # and doesn't treat symlinks to files and the files themselves as
    # different things.

    # We use a bit of a brute force approach. The directory tree is walked and
    # we get a representation of every file in it with repr_file() This
    # includes the files full text.

    old_pwd = os.getcwd()
    os.chdir(path)

    r = set(())

    for root, dirs, files in os.walk('.'):
        for f in files:
            r.add(repr_file(os.path.join(root,f)))

    os.chdir(old_pwd)
    return frozenset(r)

def check_dataset(name):
    """Check that the working dataset is identical to a given dataset.
    
    By identical we mean that every files contents are the same and the
    directory structure is the same. Symlinks are considered to be different
    than the files they point to.
    """

    return repr_dirtree(dataset_path(name)) == repr_dirtree(tmpd)

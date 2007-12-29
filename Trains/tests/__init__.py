# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2007 Peter Todd <pete@petertodd.org>
# (c) 2004 Lele Gaifax <lele@nautilus.homeip.net>
# From tailor test suite.
#
# This program is made available under the GNU GPL version 2.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

import sys
from unittest import TestProgram, TestSuite

import common

DEBUG = False

from meta import *
from Trains.tests.network import *
from Trains.tests.Generator.network import *

class trainsTest(TestProgram):
    """A command-line program that runs a set of tests; this is primarily
       for making test modules conveniently executable.
    """
    USAGE = """\
Usage: %(progName)s [options] [test] [...]

Options:
  -h, --help       Show this message
  -v, --verbose    Verbose output
  -d, --debug      Debug output
  -q, --quiet      Minimal output
  -l, --list       List available tests without running them

Examples:
  %(progName)s                               - run default set of tests
  %(progName)s MyTestSuite                   - run suite 'MyTestSuite'
  %(progName)s MyTestCase.testSomething      - run MyTestCase.testSomething
  %(progName)s MyTestCase                    - run all 'test*' test methods
                                               in MyTestCase
"""

    def __init__(self,args):
        # Create a temp directory to play in
        TestProgram.__init__(self, module='Trains.tests', argv=args)

    def parseArgs(self, argv):
        import getopt
        try:
            options, args = getopt.getopt(argv[1:], 'hHvdql',
                                          ['help','verbose','debug','quiet','list'])
            listonly = False
            for opt, value in options:
                if opt in ('-h','-H','--help'):
                    self.usageExit()
                if opt in ('-q','--quiet'):
                    self.verbosity = 0
                if opt in ('-v','--verbose'):
                    self.verbosity = 2
                if opt in ('-d','--debug'):
                    global DEBUG
                    DEBUG = True
                if opt in ('-l','--list'):
                    listonly = True
            if len(args) == 0 and self.defaultTest is None:
                self.test = self.testLoader.loadTestsFromModule(self.module)
            else:
                if len(args) > 0:
                    self.testNames = args
                else:
                    self.testNames = (self.defaultTest,)
                self.createTests()
            if listonly:
                def listsuite(suite):
                    tcount = 0
                    scount = 0
                    tclass = None
                    for t in suite._tests:
                        if isinstance(t, TestSuite):
                            tc,sc = listsuite(t)
                            tcount += tc
                            scount += sc + 1
                        else:
                            tcount += 1
                            if tclass <> t.__class__:
                                tclass = t.__class__
                                title = tclass.__name__
                                if tclass.__doc__:
                                    title += ': ' + tclass.__doc__.strip()
                                print
                                print title
                                print '='*len(title)
                            if sys.version_info >= (2, 5):
                                methodname = t._testMethodName
                            else:
                                methodname = t._TestCase__testMethodName
                            print methodname, '--',
                            print t.shortDescription()
                    return tcount, scount
                tcount, scount = listsuite(self.test)
                print
                print "%d tests in %d suites" % (tcount,scount)
                sys.exit(0)
        except getopt.error, msg:
            self.usageExit(msg)

main = trainsTest 

#!/usr/bin/env python

import sys, os, getopt
from distutils.core import setup

from Example.main import __version__ as VERSION

if sys.version_info[:2] < (2,4):
	print "Sorry, example requires version 2.4 or later of python"
	sys.exit(1)

setup(name="example",
	  version=VERSION,
	  description="Example project in python.",
	  author="Peter Todd",
	  author_email="pete@petertodd.org",
	  url="http://petertodd.org/tech/example-projects",
	  packages = ['Example'],
	  scripts = ['example'],
	  data_files = [('share/man/man1', ['example.1',]),
			('share/doc/example',
					 ['COPYING', 'README'])])


# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2007 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 2.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

__version__ = "0.0"

def main(argv):
    """
    Script entry point.

    Parse the command line options.
    """
    global __version__

    from optparse import OptionParser

    parser = OptionParser(usage="usage: %prog [OPTION...] command [ARG...]",version=__version__)

    parser.set_defaults(message="Hello World!")

    parser.add_option("--message","-m",
            action="store", type="string", dest="message",
            help="set message to display, defaults to %default")

    (options, args) = parser.parse_args(argv)

    print options.message

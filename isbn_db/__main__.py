#!/usr/bin/env python

import argparse
import sys


parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
parser.add_argument('-c', '--config', action='store', help="Use this config file on top of the base config", default='local')
parser.add_argument('-d', '--debug', action='store_true', help="Log debug messages", default=False)
parser.add_argument('-q', '--quiet', action='store_true', help="Less verbose output", default=False)
subparsers = parser.add_subparsers()

###
subparse = subparsers.add_parser('http', help='Run the http server')
subparse.set_defaults(func='http')

###
subparse = subparsers.add_parser('shell', help='Launch IPython')
subparse.set_defaults(func='shell')


args = parser.parse_args()

from . import setup
setup(args)

from . import commands

sys.exit(getattr(commands, getattr(args, 'func', 'default'))(**args.__dict__) or 0)

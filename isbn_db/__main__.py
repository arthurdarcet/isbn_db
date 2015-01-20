#!/usr/bin/env python

import argparse
import sys
import tornado.ioloop


parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
parser.add_argument('-c', '--config', action='store', help="Use this config file on top of the base config", default='local')
parser.add_argument('-d', '--debug', action='store_true', help="Log debug messages", default=False)
parser.add_argument('-q', '--quiet', action='store_true', help="Less verbose output", default=False)
subparse = parser.add_subparsers().add_parser('http', help='Run the http server')

args = parser.parse_args()

from . import setup
setup(args)

from . import config
from . import http

http.Application().listen(config.http.port, address=config.http.host)
tornado.ioloop.IOLoop.current().start()

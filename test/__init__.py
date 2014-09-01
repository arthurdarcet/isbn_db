import os.path
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from isbn_db import config
from isbn_db import setup

class args:
	config = 'base'
	debug = False
	quiet = True

setup(args)

import logging

from . import http as http_module


logger = logging.getLogger(__name__)

def shell(**kwargs):
	import IPython
	IPython.embed()

def http(**kwargs):
	http_module.Server(**kwargs).start()
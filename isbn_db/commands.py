from . import http as http_module


def shell(**kwargs):
	import IPython
	IPython.embed()

def http(**kwargs):
	http_module.Server(**kwargs).start()

default = http

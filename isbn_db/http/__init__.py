import cherrypy

from .. import config
from . import root


class Server:
	def __init__(self, **kwargs):
		cherrypy.config.update({
			'server.socket_host': config.http.host,
			'server.socket_port': config.http.port,
			'engine.autoreload.on': config.debug,
			'log.screen': False,
		})
		for module in (root, ):
			module.App().mount()
	
	def start(self):
		cherrypy.engine.start()
		cherrypy.engine.block()

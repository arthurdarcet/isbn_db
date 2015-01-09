import logging
import os.path
import tornado.web

from .. import config
from . import api
from . import root


logger = logging.getLogger(__name__)

class Server(tornado.web.Application):
	def __init__(self, **kwargs):
		super().__init__(
			root.urls + api.urls,
			debug=config.debug,
		)
		self.listen(config.http.port, address=config.http.host)
	
	def log_request(self, handler):
		(logger.info if handler.get_status() < 500 else logger.error)(
			'%d %s %.2fms',
			handler.get_status(),
			handler._request_summary(),
			1000.0 * handler.request.request_time(),
		)

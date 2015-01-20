import logging
import tornado.web

from .. import config
from . import api
from . import root


logger = logging.getLogger(__name__)

class Application(tornado.web.Application):
	def __init__(self, **kwargs):
		super().__init__(
			root.urls + api.urls,
			debug=config.debug,
		)
	
	def log_request(self, handler):
		if handler.get_status() < 500:
			logger.info(
				'%d %s %.2fms',
				handler.get_status(),
				handler._request_summary(),
				1000.0 * handler.request.request_time(),
			)

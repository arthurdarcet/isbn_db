import cherrypy
import functools
import itertools
import json
import logging
import logging.handlers

from ..utils import *


logger = logging.getLogger(__name__)

def json_exposed(fn):
	@functools.wraps(fn)
	def wrapper(*args, **kwargs):
		try:
			code = 200
			value = fn(*args, **kwargs)
		except Model.DoesNotExist as err:
			code = 404
			value = {'status': 404, 'error': repr(err)}
		except cherrypy.HTTPError as err:
			code = err.code
			value = {'status': err.code, 'error': err.reason}
		except Exception as err:
			logger.exception('{} calling {}({})'.format(
				err.__class__.__qualname__,
				fn.__name__,
				', '.join(itertools.chain(
					(repr(a) for a in args[1:]),
					('{}={!r}'.format(k, v) for k, v in kwargs.items()),
				)),
			))
			code = 500
			value = {'status': 500, 'error': '{}: {}'.format(err.__class__.__qualname__, err)}
		cherrypy.response.headers['Content-Type'] = 'application/json'
		cherrypy.response.status = code
		return json_encoder.encode(value).encode('utf8')
	wrapper.exposed = True
	return wrapper


class MemoryHandler(logging.handlers.BufferingHandler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		formatter = logging.Formatter(
			fmt='{asctime} | {name:^31} | {levelname:^8} | {message}',
			datefmt='%H:%M:%S',
			style='{'
		)
		self.setFormatter(formatter)
	
	def emit(self, record):
		self.buffer.append(self.format(record))
		if len(self.buffer) > self.capacity:
			self.acquire()
			try:
				del(self.buffer[0])
			finally:
				self.release()


class _LogManager(cherrypy._cplogging.LogManager):
	def __init__(self):
		self.error_log = logging.getLogger('cherrypy.error')
		self.access_log = logging.getLogger('cherrypy.access')
		self.access_log_format =  '{h}, {s} "{r}"'

class BaseApp:
	def mount(self):
		app = cherrypy.Application(self, self.mount_to, self.config)
		app.log = _LogManager()
		cherrypy.tree.mount(app)
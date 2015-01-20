import axel
import bson
import datetime
import json
import logging
import logging.handlers
import threading
import tornado.web

from ..utils import json_encoder


logger = logging.getLogger(__name__)

class RequestHandler(tornado.web.RequestHandler):
	def log_exception(self, *e):
		logger.critical('Uncaught exception in %s:\n', self._request_summary(), exc_info=e)


class JsonHandler(RequestHandler):
	def prepare(self):
		if self.request.headers.get('Content-Type', '').startswith('application/json'):
			self.request.json = json.loads(self.request.body.decode('utf-8'))
	
	def set_default_headers(self):
		self.set_header('Content-Type', 'application/json; charset=UTF-8')
	
	def write(self, chunk):
		super().write(json_encoder.encode(chunk) + '\n')
	
	def write_error(self, status_code, **kwargs):
		self.write({'code': status_code, 'error': self._reason})
		self.finish()


class MetaSSEHandler(type):
	def __new__(cls, name, bases, attrs):
		attrs['connections'] = []
		attrs['on_open'] = axel.Event()
		return super().__new__(cls, name, bases, attrs)

class JsonSSEHandler(RequestHandler, metaclass=MetaSSEHandler):
	def set_default_headers(self):
		self.set_header('Content-Type','text/event-stream; charset=utf-8')
		self.set_header('Cache-Control','no-cache')
		self.set_header('Connection','keep-alive')
	
	@tornado.web.asynchronous
	def get(self):
		self.connections.append(self)
		logger.debug('New event listener %s (has %s clients)', self, len(self.connections))
		self.on_open()
	
	@tornado.gen.coroutine
	def on_open(self):
		pass
	
	def on_connection_close(self):
		self.connections.remove(self)
		logger.debug('Removed event listener %s (has %s clients)', self, len(self.connections))
	
	@classmethod
	@tornado.gen.coroutine
	def broadcast(cls, *args, **kwargs):
		for conn in cls.connections:
			yield conn.emit(*args, **kwargs)
	
	@tornado.gen.coroutine
	def emit(self, data, event=None):
		if event is not None:
			self.write('event: {}\n'.format(event))
		self.write('data: {}\n\n'.format(json.dumps(data)))
		yield self.flush()


class EventsLogHandler(logging.Handler):
	def __init__(self, capacity):
		super().__init__()
		self.on_log = axel.Event()
		self.buffer = []
		self.capacity = capacity
		self.formatter = logging.Formatter(
			fmt='{asctime} | {name:^15} | {levelname:^8} | {message}',
			datefmt='%H:%M:%S',
			style='{'
		)
	
	def emit(self, record):
		msg = self.format(record)
		self.on_log(msg)
		self.buffer.append(msg)
		if len(self.buffer) > self.capacity:
			# no need to use a lock, see https://hg.python.org/cpython/file/350b8e109c42/Lib/logging/__init__.py
			del(self.buffer[0])

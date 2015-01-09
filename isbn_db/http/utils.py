import axel
import bson
import datetime
import json
import logging
import logging.handlers
import threading
import tornado.web


logger = logging.getLogger(__name__)

class JSONEncoder(json.JSONEncoder):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault('separators', (',', ':'))
		super().__init__(*args, **kwargs)
	
	def default(self, o):
		if isinstance(o, datetime.datetime):
			return o.isoformat()
		if isinstance(o, bson.ObjectId):
			return str(o)
		try:
			iterable = iter(o)
		except TypeError:
			pass
		else:
			return list(iterable)
		return super().default(o)
json_encoder = JSONEncoder()


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
		self.on_open(self)
	
	def on_open(self):
		pass
	
	def on_finish(self):
		self.connections.remove(self)
	
	@classmethod
	def broadcast(cls, *args, **kwargs):
		for conn in cls.connections:
			conn.emit(*args, **kwargs)
	
	def emit(self, data, event=None):
		if event is not None:
			self.write('event: {}\n'.format(event))
		self.write('data: {}\n\n'.format(json.dumps(data)))
		self.flush()


class EventsLogHandler(logging.Handler):
	def __init__(self, capacity):
		super().__init__()
		self.on_log = axel.Event()
		self.lock = threading.Lock()
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
			with self.lock:
				del(self.buffer[0])

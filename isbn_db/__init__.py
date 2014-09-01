import logging as _logging
import logging.config as _logging_config
import os.path
import sys
import yaml


class _config(dict):
	cli_flags = 'debug', 'quiet'
	
	def load(self, cfg):
		path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', cfg + '.yaml')
		if os.path.exists(path):
			with open(path, 'r') as f:
				self.update(self.create(yaml.load(f)))
	
	@classmethod
	def create(cls, o):
		if isinstance(o, (list, tuple)):
			return [cls.create(x) for x in o]
		elif isinstance(o, dict):
			return cls({k: cls.create(v) for k, v in o.items()})
		else:
			return o
	
	def __getattr__(self, k):
		try:
			return self[k]
		except KeyError as err:
			raise AttributeError(err) from err
	
	def __setattr__(self, k, v):
		self[k] = v
	
	def __delattr__(self, k):
		if k in self:
			del self[k]
	
	def __setitem__(self, k, v):
		super().__setitem__(k, self.create(v))
	
	def setup(self, args):
		self.load('base')
		self.load(args.config)
		for k in self.cli_flags:
			self[k] = getattr(args, k)

config = _config()


class logging:
	@staticmethod
	def setup():
		cfg = {
			'version': 1,
			'handlers': {
				'console': {
					'class': 'logging.StreamHandler',
					'formatter': 'clean',
				},
			},
			'formatters': {
				'clean': {
					'format' : '{asctime} | {name:^20} | {levelname:^8} | {message}',
					'datefmt' : '%Y-%m-%d %H:%M:%S',
					'style': '{',
				},
			},
			'loggers': {
				__name__: {
					'level': 'DEBUG' if config.debug else 'INFO' if not config.quiet else 'WARNING',
				},
			},
			'root': {
				'handlers': ['console'],
			}
		}
		
		_logging_config.dictConfig(cfg)
		_logging.captureWarnings(True)

sys.excepthook = lambda *e, _logging=_logging: _logging.critical('Uncaught %s: %s', e[0].__qualname__, e[1], exc_info=e)


def setup(args=None):
	if args is not None:
		config.args = args
		config.setup(config.args)
	logging.setup()

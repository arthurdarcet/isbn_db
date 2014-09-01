import cherrypy
import logging
import os.path

from ..book import Book
from . import utils


class App(utils.BaseApp):
	mount_to = '/'
	static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
	
	config = {
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': static_dir,
		},
		'/index': {
			'tools.staticfile.on': True,
			'tools.staticfile.filename': os.path.join(static_dir, 'index.html'),
		},
	}
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._logs = utils.MemoryHandler(500)
		src_logger = logging.getLogger(__name__.split('.')[0])
		src_logger.addHandler(self._logs)
	
	@utils.json_exposed
	def logs(self):
		return self._logs.buffer[::-1]
	
	@utils.json_exposed
	def books(self, page=0):
		try:
			page = int(page)
		except TypeError:
			raise cherrypy.NotFound()
		
		books = list(Book.objects.find().sort('isbn', 1).skip(page * 50).limit(50))
		return [b.json for b in books]

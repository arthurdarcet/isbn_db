import cherrypy
import logging
import os.path

from ..models import Book
from ..models import ISBN
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
		
		return Book.objects.find().sort('isbn', 1).skip(page * 50).limit(50)
	
	@utils.json_exposed
	def add_book(self, title, authors=None, identifiers=None):
		if authors is None:
			authors = []
		if not isinstance(authors, list):
			authors = [authors]
		if identifiers is None:
			identifiers = []
		if not isinstance(identifiers, list):
			identifiers = [identifiers]
		
		try:
			return Book.objects.get(identifiers={'$in': identifiers})
		except Book.DoesNotExist:
			try:
				book = Book.objects.get(title=title, authors=authors)
			except Book.DoesNotExist:
				isbn = ISBN.free()
				book = Book(title=title, authors=authors, identifiers=identifiers, isbn=isbn['isbn'])
				isbn['book'] = book['_id']
				isbn.save()
			else:
				book['identifiers'] += identifiers
			book.save()
			return book
	
	@utils.json_exposed
	def add_isbn(self, start, end=None):
		return {'added': ISBN.add(start, end or start)}

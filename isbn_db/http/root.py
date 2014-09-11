import cherrypy
import logging
import os.path

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
		
		return ISBN.objects \
			.find({'book': {'$exists': True}}) \
			.sort('isbn', 1) \
			.skip(page * 50) \
			.limit(50)
	
	@utils.json_exposed
	def search(self, q):
		return ISBN.objects.find({'$or': [
			{a: {'$regex': q, '$options': 'i'}}
			for a in ('isbn', 'book.title', 'book.authors', 'book.identifiers')
		]})
	
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
			return ISBN.objects.get(**{'book.identifiers': {'$in': identifiers}})
		except ISBN.DoesNotExist:
			isbn = ISBN.free()
			isbn['book'] = {'title': title, 'authors': authors, identifiers: 'identifiers'}
			isbn.save()
			return isbn
	
	@utils.json_exposed
	def add_isbn(self, start, end=None):
		return {'added': ISBN.add(start, end or start)}

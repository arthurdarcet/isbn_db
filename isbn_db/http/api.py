import logging

from ..models import ISBN
from . import utils


class Books(utils.JsonHandler):
	def get(self):
		q = self.get_query_argument('q', '')
		query = None
		
		if len(q) in (12, 13):
			try: int(q)
			except ValueError: pass
			else:
				if len(q) == 12: q += str(ISBN.checksum(q))
				query = {'_id': int(q)}
		
		if query is None and q:
			query = {'$or': [
				{a: {'$regex': q, '$options': 'i'}}
				for a in ('book.title', 'book.authors', 'book.identifiers')
			]}
		else:
			query = {'book': {'$exists': True}}
		
		page = int(self.get_query_argument('page', 0))
		self.write(ISBN.objects.find(query).sort('_id', 1).skip(page * 50).limit(50))
	
	def post(self):
		try:
			isbn = ISBN.objects.get(**{
				'book.identifiers': {'$in': self.get_body_arguments('identifiers')},
			})
		except ISBN.DoesNotExist:
			isbn = ISBN.free()
			isbn['book'] = {
				'title': self.get_body_argument('title'),
				'authors': self.get_body_arguments('authors'),
				'identifiers': self.get_body_arguments('identifiers'),
			}
			isbn.save()
		self.write(isbn)


class ISBNs(utils.JsonHandler):
	def post(self):
		start = self.get_body_argument('start')
		end = self.get_body_argument('end', '')
		if len(end) == 12:
			end += '?'
		if len(start) == 12:
			start += str(ISBN.checksum(start))
		if not end:
			end = start
		if len(start) != 13 or int(start[-1]) != ISBN.checksum(start) or len(end) != 13 or start[:3] != end[:3]:
			raise ValueError('Invalid ISBN range ({}, {})'.format(start, end))
		
		self.write({'added': ISBN.add(start, end)})


class Events(utils.JsonSSEHandler):
	pass


mem_log = utils.EventsLogHandler(500)
logging.root.addHandler(mem_log)
def backlog(conn):
	for l in mem_log.buffer:
		conn.emit(l, event='log')
Events.on_open += backlog
mem_log.on_log += lambda msg: Events.broadcast(msg, event='log')

urls = [
	(r'/events', Events),
	
	(r'/books', Books),
	(r'/isbns', ISBNs),
]

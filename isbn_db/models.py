import logging

from . import utils


logger = logging.getLogger(__name__)

class Book(utils.Model):
	collection = 'books'

class ISBN(utils.Model):
	collection = 'isbns'
	
	@classmethod
	def free(cls):
		res = cls.objects.find_one(book=None)
		if res is None:
			raise ValueError('No more free isbns in the DB')
		return res
	
	@classmethod
	def add(cls, start, end):
		res = 0
		for isbn in range(int(start[:-1]), int(end[:-1]) + 1):
			res += 1
			cls(isbn=isbn + cls.checksum(str(isbn))).save()
		logger.info('Added %d ISBNs to the DB', res)
		return res
	
	@staticmethod
	def checksum(I):
		return (10 - (sum(int(I[2*i]) + 3*int(I[2*i+1]) for i in range(6)) % 10)) % 10

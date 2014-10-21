import logging

from . import utils


logger = logging.getLogger(__name__)

class ISBN(utils.Model):
	collection = 'isbns'
	
	@classmethod
	def free(cls):
		res = cls.objects.find_one({'book': None})
		if res is None:
			raise ValueError('No more free isbns in the DB')
		return res
	
	@classmethod
	def add(cls, start, end):
		res = cls.objects.insert([
			cls(_id=int('{}{}'.format(isbn, cls.checksum(isbn))))
			for isbn in range(int(start[:-1]), int(end[:-1]) + 1)
		])
		logger.info('Added %d ISBNs to the DB', len(res))
		return len(res)
	
	@staticmethod
	def checksum(I):
		I = str(I)
		return (10 - (sum(int(I[2*i]) + 3*int(I[2*i+1]) for i in range(6)) % 10)) % 10

import unittest

from nose2.tools import params

from isbn_db.models import ISBN


class TestISBN(unittest.TestCase):
	@params(
		'9782954657707',
		'9782954657714',
		'9782954657721',
		'9782954657738',
		'9782954657745',
	)
	def test_checksum(self, isbn):
		self.assertEquals(ISBN.checksum(isbn), int(isbn[-1]))

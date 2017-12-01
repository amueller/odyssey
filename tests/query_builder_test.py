import unittest
from odyssey.utils.query_builder import *

class TestQueryBuilder(unittest.TestCase):

	def test_connect_with_and(self):
		self.assertEqual(connect_with_and(), "")
		self.assertEqual(connect_with_and(""), "")
		self.assertEqual(connect_with_and("", ""), "")
		contains_sklearn = 'contents CONTAINS "sklearn"'
		contains_svc = 'contents CONTAINS "SVC"'
		target = '(%s) AND (%s)' % (contains_sklearn, contains_svc)
		self.assertEqual(connect_with_and(contains_sklearn, 
			contains_svc), target)
		self.assertEqual(connect_with_and("  ", contains_sklearn, "",
			contains_svc, " "), target)

	def test_connect_with_or(self):
		self.assertEqual(connect_with_or(), "")
		self.assertEqual(connect_with_or(""), "")
		self.assertEqual(connect_with_or("", ""), "")
		contains_sklearn = 'contents CONTAINS "sklearn"'
		contains_svc = 'contents CONTAINS "SVC"'
		target = '(%s) OR (%s)' % (contains_sklearn, contains_svc)
		self.assertEqual(connect_with_or(contains_sklearn, 
			contains_svc), target)
		self.assertEqual(connect_with_or("  ", contains_sklearn, "",
			contains_svc, " "), target)

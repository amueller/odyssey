import unittest
from odyssey.core.analyzer.ImportAnalyzer import ImportAnalyzer
from .BigQueryGithubEntry_test import BigQueryGithubEntryMock

class TestImportAnalyzer(unittest.TestCase):

	def test_instantiation(self):
		a = ImportAnalyzer("sklearn", [])
		self.assertEqual(a.package, "sklearn")
		self.assertEqual(a.accepted_list, [])
		b = ImportAnalyzer("sklearn", "SKLEARN_ALL")
		# model/submodule/function all included
		self.assertTrue("SVC" in b.accepted_list)
		self.assertTrue("train_test_split" in b.accepted_list)
		self.assertTrue("tree" in b.accepted_list)

	def test_parse_real(self):
		a = ImportAnalyzer("sklearn", "SKLEARN_ALL")
		a.parse(BigQueryGithubEntryMock())
		self.assertTrue("KMeans" in a.counter)

	def test_parse_test1(self):
		a = ImportAnalyzer("sklearn", ['A', 'B'])
		code = """\
from sklearn.A import B
"""
		a.parse(BigQueryGithubEntryMock(code))
		self.assertTrue(len(a.counter["A"]) == 1)
		self.assertTrue(len(a.counter["B"]) == 1)

	def test_parse_test2(self):
		a = ImportAnalyzer("sklearn", ['A', 'B'])
		code = """\
from sklearn import A
from sklearn import B
"""
		a.parse(BigQueryGithubEntryMock(code))
		self.assertTrue(len(a.counter["A"]) == 1)
		self.assertTrue(len(a.counter["B"]) == 1)

	def test_parse_test3(self):
		a = ImportAnalyzer("sklearn", ['A', 'B'])
		code = """\
from sklearn import A, B
"""
		a.parse(BigQueryGithubEntryMock(code))
		self.assertTrue(len(a.counter["A"]) == 1)
		self.assertTrue(len(a.counter["B"]) == 1)

	def test_parse_test4(self):
		a = ImportAnalyzer("sklearn", ['A', 'B'])
		code = """\
from sklearn import A, B as C
"""
		a.parse(BigQueryGithubEntryMock(code))
		self.assertTrue(len(a.counter["A"]) == 1)
		self.assertTrue(len(a.counter["B"]) == 1)

	def test_parse_test5(self):
		a = ImportAnalyzer("sklearn", ['A', 'B'])
		code = """\
from sklearn import A as X
from sklearn import B as Y
"""
		a.parse(BigQueryGithubEntryMock(code))
		self.assertTrue(len(a.counter["A"]) == 1)
		self.assertTrue(len(a.counter["B"]) == 1)

	def test_parse_test6(self):
		a = ImportAnalyzer("sklearn", ['A', 'B'])
		code = """\
import sklearn.A
import sklearn.B
"""
		a.parse(BigQueryGithubEntryMock(code))
		self.assertTrue(len(a.counter["A"]) == 1)
		self.assertTrue(len(a.counter["B"]) == 1)

	def test_parse_test7(self):
		a = ImportAnalyzer("sklearn", ['A', 'B'])
		code = """\
import sklearn.A as X
import sklearn.B as Y
"""
		a.parse(BigQueryGithubEntryMock(code))
		self.assertTrue(len(a.counter["A"]) == 1)
		self.assertTrue(len(a.counter["B"]) == 1)
	
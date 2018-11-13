import unittest
from odyssey.core.bigquery.GithubPython import GithubPython


class TestGithubPython(unittest.TestCase):

	def test_instantiation(self):
		a = GithubPython()
		self.assertTrue(a.package == "")
		self.assertEqual(a.exclude_forks, "auto")
		b = GithubPython("sklearn", False)
		self.assertTrue(b.package == "sklearn")
		self.assertFalse(b.exclude_forks == True)

	def test_build_exclude_repo_string(self):
		a = GithubPython("sklearn")
		self.assertEqual(a._contains_package_string(),
			'REGEXP_CONTAINS(content, "sklearn")')

	def test_get_query(self):
		a = GithubPython("sklearn", False)
		self.assertTrue("content, repo_name, path"
			in a._get_all_query())
		self.assertTrue('REGEXP_CONTAINS(content,"sklearn"')
			in a._get_all_query())
		self.assertTrue("count(*)" in a._get_count_query())

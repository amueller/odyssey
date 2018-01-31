"""
GithubPython.py
====================================
The module for using Google BigQuery on Github Data.

"""

from odyssey.utils.query_builder import connect_with_and, connect_with_or
from odyssey.core.analyzer import RepoImportCounter, ImportAnalyzer, InstantiationAnalyzer
from odyssey.core.bigquery.BigQueryGithubEntry import BigQueryGithubEntry
from joblib import Memory

memory = Memory(cachedir=".",verbose=0)

class GithubPython:
	"""Provides functionality to build SQL query, connect with BigQuery, etc."""

	PY_FILE_UNIQUE = '`Odyssey_github_sklearn.content_py_unique`'
	PY_FILE_ALL = '`Odyssey_github_sklearn.content_py_full`'

	def __init__(self, package="", exclude_forks="auto", limit=None):
		"""Initialize the GithubPython object.
		
		Parameters
		----------
		package : string
			Name of python package you are interested in using Odyssey to analyze.
		
		exclude_forks : string, list or tuple, optional (default="auto")
			In SQL query, exclude both path that contains exclude_forks and repo_name that contains exclude_forks.
			If exclude_forks is auto, it is set to a list that contains package name.

		limit : int or None
			Limit your analysis to a certain amount of results. Usually set for billing limit or performance reason.
		
		Returns
		-------

		object
			returns an initialized GithubPython object.

		"""
		self._reset(package)
		self.exclude_forks = exclude_forks
		self.limit = limit
		self.get_all = memory.cache(self.get_all)
		self.get_count = memory.cache(self.get_count)
		self.class_list = self.submodule_list = self.function_list = None


	def _reset(self, package):
		"""Reset package attribute and import analyzers when package is reset."""
		self.package = package
		self.ia_class = ImportAnalyzer(package, [])
		self.ia_submodule = ImportAnalyzer(package, [])
		self.ia_function = ImportAnalyzer(package, [])

	def get_all(self, _filter=None):
		"""Get all data (id, code, repo_name and path) subject to filter.
		
		Parameters
		----------
		_filter : Filter object or None, optional (default=None)
			Filter the result as defined in the filter object.

		Returns
        -------
        list
            Returns a list of BigQueryGithubEntry object

		"""
		res = self.run(self._get_all_query(_filter))
		return [BigQueryGithubEntry(_id, code, repo_name, path) for _id, code, repo_name, path in res]

	def get_count(self, _filter=None):
		"""Get count of files subject to filter.
		
		Parameters
		----------
		_filter : Filter object or None, optional (default=None)
			Filter the result as defined in the filter object.

		Returns
        -------
        int
            Returns an integer for count.

		"""
		return self.run(self._get_count_query(_filter))[0][0]

	def get_top_import_repo(self,n=None, _filter=None):
		"""Get top imported repo. See RepoImportCounter for details.
		
		Parameters
		----------
		n : int or None, optional (default=None)
			the top n most imported repo name to be returned. If set to None, all results will be returned.

		Returns
        -------
        list
            Returns a list of repo name.

		"""
		entries = self.get_all(_filter)
		ric = RepoImportCounter(self.package)
		i = 0
		for entry in entries:
			if (i%1000 == 0):
				print(i)
			ric.parse(entry)
			i += 1
		return ric.get_most_common(n)

	# The following functions are related to ImportAnalyzer
	def set_class_list(self, L):
		"""Set class list which will be used for ImportAnalyzer to classify import.
		
		Parameters
		----------
		L : list of string
			class list that should be identified by ImportAnalyzer.

		"""
		self.class_list = L

	def set_submodule_list(self, L):
		"""Set submodule list which will be used for ImportAnalyzer to classify import.
		
		Parameters
		----------
		L : list of string
			submodule list that should be identified by ImportAnalyzer.

		"""
		self.submodule_list = L

	def set_function_list(self, L):
		"""Set function list which will be used for ImportAnalyzer to classify import.
		
		Parameters
		----------
		L : list of string
			function list that should be identified by ImportAnalyzer.

		"""
		self.function_list = L

	def _get_most_imported_helper(self, ia_to_use, n, use_count_less_than=None, use_count_more_than=None, _filter=None):
		accepted_list = self._get_accepted_list(ia_to_use) if self._get_accepted_list(ia_to_use) else self.package.upper() + '_' + ia_to_use
		f = None
		if not (use_count_more_than is None) and not (use_count_less_than is None):
			f = lambda x: x[1] < use_count_less_than and x[1] > use_count_more_than
		elif not (use_count_more_than is None):
			f = lambda x: x[1] > use_count_more_than
		elif not (use_count_less_than is None):
			f = lambda x: x[1] < use_count_less_than
		return self._get_imported_info(n, _filter, accepted_list, ia_to_use, f)

	def _get_accepted_list(self, ia_to_use):
		if ia_to_use == "CLASS":
			return self.class_list
		elif ia_to_use == "SUBMODULE":
			return self.submodule_list
		elif ia_to_use == "FUNCTION":
			return self.function_list
		else:
			print("Wrong ia_to_use value! " % ia_to_use)
			return []

	def get_most_imported_class(self, n=None, use_count_less_than=None, use_count_more_than=None, _filter=None):
		"""Get n most imported classes within a certain use count range, subject to filter.
		
		Parameters
		----------
		n : int or None, optional (default=None)
			the top n most imported classes to be returned. If set to None, all results will be returned.
		use_count_less_than : int or None, optional (default=None)
			only include classes that have use count less than this amount. If none, there will be no restriction.
		use_count_more_than : int or None, optional (default=None)
			only include classes that have use count more than this amount. If none, there will be no restriction.
		_filter : Filter object or None (default=None)
			Filter the result as defined in the filter object.

		Returns
		-------
		list
			Returns a list of tuple (name, count)

		"""
		return self._get_most_imported_helper("CLASS", n, use_count_less_than, use_count_more_than, _filter)

	def get_least_imported_class(self, n=None, use_count_less_than=None, use_count_more_than=None, _filter=None):
		"""Get n least imported class within a certain use count range, subject to filter.
		
		Parameters
		----------
		n : int or None, optional (default=None)
			the top n least imported classes to be returned. If set to None, all results will be returned.
		use_count_less_than : int or None, optional (default=None)
			only include classes that have use count less than this amount. If none, there will be no restriction.
		use_count_more_than : int or None, optional (default=None)
			only include classes that have use count more than this amount. If none, there will be no restriction.
		_filter : Filter object or None (default=None)
			Filter the result as defined in the filter object.

		Returns
		-------
		list
			Returns a list of tuple (name, count)

		"""
		return self._get_most_imported_helper("CLASS", -n, use_count_less_than, use_count_more_than, _filter)

	def get_most_imported_submodule(self, n=None, use_count_less_than=None, use_count_more_than=None, _filter=None):
		"""Get n most imported submodule within a certain use count range, subject to filter.
		
		Parameters
		----------
		n : int or None, optional (default=None)
			the top n least imported submodule to be returned. If set to None, all results will be returned.
		use_count_less_than : int or None, optional (default=None)
			only include submodules that have use count less than this amount. If none, there will be no restriction.
		use_count_more_than : int or None, optional (default=None)
			only include submodules that have use count more than this amount. If none, there will be no restriction.
		_filter : Filter object or None (default=None)
			Filter the result as defined in the filter object.
	
		Returns
		-------
		list
			Returns a list of tuple (name, count)

		"""
		return self._get_most_imported_helper("SUBMODULE", n, use_count_less_than, use_count_more_than, _filter)

	def get_least_imported_submodule(self, n=None, use_count_less_than=None, use_count_more_than=None, _filter=None):
		"""Get n least imported submodule within a certain use count range, subject to filter.
		
		Parameters
		----------
		n : int or None, optional (default=None)
			the top n least imported submodule to be returned. If set to None, all results will be returned.
		use_count_less_than : int or None, optional (default=None)
			only include submodules that have use count less than this amount. If none, there will be no restriction.
		use_count_more_than : int or None, optional (default=None)
			only include submodules that have use count more than this amount. If none, there will be no restriction.
		_filter : Filter object or None (default=None)
			Filter the result as defined in the filter object.

		Returns
		-------
		list
			Returns a list of tuple (name, count)

		"""
		return self._get_most_imported_helper("SUBMODULE", -n, use_count_less_than, use_count_more_than, _filter)

	def get_most_imported_function(self, n=None, use_count_less_than=None, use_count_more_than=None, _filter=None):
		"""Get n most imported function within a certain use count range, subject to filter.
		
		Parameters
		----------
		n : int or None, optional (default=None)
			the top n least imported function to be returned. If set to None, all results will be returned.
		use_count_less_than : int or None, optional (default=None)
			only include functions that have use count less than this amount. If none, there will be no restriction.
		use_count_more_than : int or None, optional (default=None)
			only include functions that have use count more than this amount. If none, there will be no restriction.
		_filter : Filter object or None (default=None)
			Filter the result as defined in the filter object.

		Returns
		-------
		list
			Returns a list of tuple (name, count)

		"""
		return self._get_most_imported_helper("FUNCTION", n, use_count_less_than, use_count_more_than, _filter)

	def get_least_imported_function(self, n=None, use_count_less_than=None, use_count_more_than=None, _filter=None):
		"""Get n least imported function within a certain use count range, subject to filter.
		
		Parameters
		----------
		n : int or None, optional (default=None)
			the top n least imported function to be returned. If set to None, all results will be returned.
		use_count_less_than : int or None, optional (default=None)
			only include functions that have use count less than this amount. If none, there will be no restriction.
		use_count_more_than : int or None, optional (default=None)
			only include functions that have use count more than this amount. If none, there will be no restriction.
		_filter : Filter object or None (default=None)
			Filter the result as defined in the filter object.

		Returns
		-------
		list
			Returns a list of tuple (name, count)

		"""
		return self._get_most_imported_helper("FUNCTION", -n, use_count_less_than, use_count_more_than, _filter)

	def _get_imported_info(self, n, _filter, accepted_list, ia_to_use, f=None):
		ia = ImportAnalyzer(self.package, accepted_list)
		entries = self.get_all(_filter)
		for entry in entries:
			ia.parse(entry)
		if ia_to_use == "CLASS":
			self.ia_class = ia
		elif ia_to_use == "SUBMODULE":
			self.ia_submodule = ia
		elif ia_to_use == "FUNCTION":
			self.ia_function = ia
		else:
			print("Wrong ia_to_use value! " % ia_to_use)
		if f:
			return ia.get_by_filter(f)
		if n >= 0:
			return ia.get_most_common(n)
		else:
			return ia.get_least_common(-n)

	def get_import_source(self, val):
		"""Returns a list of BigQueryGithubEntry that imported val.
		
		Parameters
		----------
		val : string
			The class/submodule/function to examine sources file on
	
		Returns
		-------
		list
			Returns a list of BigQueryGithubEntry
		"""
		return self.ia_class.get_source(val) + self.ia_submodule.get_source(val) + self.ia_function.get_source(val)

	def set_package(self, package):
		"""Reset package name.
		
		Parameters
		----------
		package: string
			See doc of __init__ for definition of package attribute.

		"""
		self._reset(package)

	def set_exclude_forks(self, exclude_forks):
		"""Reset exclude_forks.
		
		Parameters
		----------
		exclude_forks: list or None
			See doc of __init__ for definition of exclude_forks attribute.

		"""
		self.set_exclude_forks = exclude_forks

	def set_limit(self, limit):
		"""Reset limit.
		
		Parameters
		----------
		limit: int
			See doc of __init__ for definition of limit attribute.

		"""
		self.limit = limit

	def run(self, query, project="odyssey-193217"):
		"""Run SQL query with Google BigQuery. Allow large results. Timeout set to 99999999.
		
		Parameters
		----------
		query: string
			SQL query to be executed.

		project: string, optional (default="odyssey-193217")
			Project to run the query on (for billing, logging, etc. purpose)

		Returns
		-------
		list
			Returns result in python list.

		"""
		from google.cloud import bigquery
		job_config = bigquery.QueryJobConfig()
		client = bigquery.Client(project=project)
		result = client.query(query,job_config=job_config)
		job_config.allowLargeResults = True
		result.__done_timeout = 99999999
		return list(result)

	def _get_query(self, select, _filter=None):
		where_clause = ""
		if _filter or self.package:
			_filter_string = str(_filter) if _filter else ""
			where_clause = "WHERE "
			where_clause += connect_with_and(
					_filter_string, 
					self._contains_package_string(),
					*self._exclude_forks_string_list()
			)

		limit_clause = ""
		if self.limit:
			limit_clause = "LIMIT %s" % self.limit

		query = """
		SELECT
			%s
		FROM
			%s
		%s
		%s
		""" % (select, GithubPython.PY_FILE_UNIQUE, where_clause, limit_clause)
		return query

	def _get_all_query(self, _filter=None):
		return self._get_query("id, content, repo_name, path", _filter)

	def _get_count_query(self, _filter=None):
		return self._get_query("count(*)", _filter)

	def _contains_package_string(self):
		return 'REGEXP_CONTAINS(content,"%s")' % self.package

	def _contains_package_string_standard_sql(self):
		return "NOT(STRPOS(content, '%s') = 0)" % self.package

	def _exclude_forks_string_list(self):
		if not self.exclude_forks:
			return ""
		exclude_list = []
		if self.exclude_forks == "auto":
			exclude_list = [self.package]
		elif type(self.exclude_forks) == list or type(Self.exclude_forks) == tuple:
			exclude_list = list(self.exclude_forks)
		else:
			print("Unsupported exclude_forks!")
		
		string_builder = []
		for keyword in exclude_list:
			string_builder.append('REGEXP_CONTAINS(path,"%s")' % keyword)
			string_builder.append('REGEXP_CONTAINS(repo_name,"%s")' % keyword)

		all_forks = '''
		SELECT DISTINCT(repo_name)
	
		FROM
			%s
		WHERE
			%s
		''' % (GithubPython.PY_FILE_ALL, connect_with_or(*string_builder))

		res = self.run(all_forks)
		excluded_repos =[ 'NOT REGEXP_CONTAINS(repo_name, "%s")' % repo_name[0]  for repo_name in res ]
		return excluded_repos

	def _exclude_forks_string_list_standard_sql(self):
		if not self.exclude_forks:
			return ""
		exclude_list = []
		if self.exclude_forks == "auto":
			exclude_list = [self.package]
		elif type(self.exclude_forks) == list or type(Self.exclude_forks) == tuple:
			exclude_list = list(self.exclude_forks)
		else:
			print("Unsupported exclude_forks!")
		
		string_builder = []
		for keyword in exclude_list:
			string_builder.append('REGEXP_CONTAINS(path,"%s")' % keyword)
			string_builder.append('REGEXP_CONTAINS(repo_name,"%s")' % keyword)

		all_forks = '''
		SELECT
			DISTINCT(repo_name)
		FROM
			%s
		WHERE
			%s
		''' % (GithubPython.PY_FILE_ALL, connect_with_or(*string_builder))

		res = self.run(all_forks)
		excluded_repos = ["STRPOS(repo_name, '%s') = 0" % repo_name[0]
			for repo_name in res]
		return excluded_repos

	def get_context(self, class_name):
		"""Get context for class usage.
		
		Parameters
		----------
		class_name: string
			Which class to examine context.

		Returns
		-------
		list
			Returns a list of tuple of (context_string, path, repo_name, count).

		"""
		return self._get_context_all(class_name)

	def get_instantiation(self, class_name):
		"""Get instantiation information for class usage.
		
		Parameters
		----------
		class_name: string
			Which class to examine instantiation.

		Returns
		-------
		dict
			Returns a nested dict: dict(key=arg, value=dict(key=value_that_arg_sets_to, value=count))

		"""
		contexts = self._get_context_all(class_name)
		analyzer = InstantiationAnalyzer(class_name)
		for i in range(1, len(contexts)):
			code = contexts[i][0]
			analyzer.parse(code)
		return analyzer.d

	def _get_context_all(self, class_name):
		limit_clause = ""
		if self.limit:
			limit_clause = "LIMIT %s" % self.limit
		query = '''
		#standardSQL
		CREATE TEMPORARY FUNCTION parsePythonFile(a STRING)
		RETURNS STRING
		LANGUAGE js AS """
		if (a === null) {
		  return null;
		}
		var lines = a.split('\\\\n');
		for (i=0;i<lines.length;i++) {
		  if (lines[i].indexOf("%s")!==-1){
			return a;
		  }
		}
		""";

		CREATE TEMPORARY FUNCTION parsePythonFile2(a STRING, b STRING)
		RETURNS STRING
		LANGUAGE js AS """
		if (a === null) {
		  return null;
		}
		var lines = a.split('\\\\n');
		for (i=0;i<lines.length;i++) {
		  if (lines[i].indexOf("%s")!==-1){
			return b;
		  }
		}
		""";

		SELECT
		parsePythonFile(content) match,
		parsePythonFile2(content,path) path,
		parsePythonFile2(content,repo_name) repo_name,
		count(*) count
		FROM   
		`Odyssey_github_sklearn.content_py_unique` 
		WHERE
		 %s
		GROUP BY
		1,2,3
		ORDER BY 
		count DESC
		''' % (class_name, class_name, connect_with_and(
					self._contains_package_string_standard_sql(),
					*self._exclude_forks_string_list_standard_sql()
			)) + limit_clause
		return self.run(query)

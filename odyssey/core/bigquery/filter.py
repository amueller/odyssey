"""
filter.py
====================================
The module that defines Filters.

"""

class Filter:
	"""Base class for other filters to inherit."""
	pass

class Contains(Filter):
	"""Require code content to contain a specific string."""
	def __init__(self, s):
		"""Initialize the Contains filter.
		
		Parameters
		----------
		s: string
			String that needs to contain in code content.
		
		Returns
		-------

		object
			returns an initialized Contains filter.

		"""
		if type(s) != str:
			raise Exception("%r should be of string type!" %s)
		self.s = s

	def __str__(self):
		"""String representation of the filter. Also the string that will appear in SQL query"""
		return "REGEXP_CONTAINS(content,'%s')" %self.s

class And(Filter):
	"""And filter takes in two filters and requires both to be true."""
	def __init__(self, f1, f2):
		"""Initialize the And filter.
		
		Parameters
		----------
		f1: Filter
			filter 1.

		f2: Filter
			filter 2.
		
		Returns
		-------

		object
			returns an initialized And filter.

		"""
		if not(isinstance(f1, Filter) and isinstance(f2, Filter)):
			raise Exception("'And' Filter takes two filters to instantiate!")
		self.f1, self.f2 = f1, f2

	def __str__(self):
		"""String representation of the filter. Also the string that will appear in SQL query"""
		return "(%s AND %s)"%(self.f1, self.f2)

class Or(Filter):
	"""Or filter takes in two filters and requires one of them to be true."""
	def __init__(self, f1, f2):
		"""Initialize the Or filter.
		
		Parameters
		----------
		f1: Filter
			filter 1.

		f2: Filter
			filter 2.
		
		Returns
		-------

		object
			returns an initialized Or filter.

		"""
		if not(isinstance(f1, Filter) and isinstance(f2, Filter)):
			raise Exception("'Or' Filter takes two filters to instantiate!")
		self.f1, self.f2 = f1, f2

	def __str__(self):
		"""String representation of the filter. Also the string that will appear in SQL query"""
		return "(%s OR %s)"%(self.f1, self.f2)

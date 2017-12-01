"""
BigQueryGithubEntry.py
====================================
The module that defines BigQueryGithubEntry class.

"""

class BigQueryGithubEntry:
	"""A struct that contains relevant information about an entry in BigQuery Github table."""
	def __init__(self, _id, code, repo_name, path):
		"""Initialize the BigQueryGithubEntry object.
		
		Parameters
		----------
		_id : string
			a hashed value representing a file entry in BigQuery Github table. This is provided in Google BigQuery Github table.

		code : string
			code string.

		repo_name : string
			name of the repo. (e.g.: scikit-learn/scikit-learn)

		path: string
			path of the file. (e.g.: doc/HOWTO_DOCUMENT.rst)
		
		Returns
		-------

		object
			returns an initialized BigQueryGithubEntry object.

		"""
		self.id = _id
		self.code = code
		self.repo_name = repo_name
		self.path = path
	
	def __str__(self):
		"""Encode the code string in utf-8 and return. For printing purpose."""
		return str(self.code.encode('utf-8'))

	def get_url(self):
		"""Returns a GitHub url linking to the file. Possibly an invalid link if the file has been removed."""
		return "https://github.com/{}/tree/master/{}".format(self.repo_name, self.path)
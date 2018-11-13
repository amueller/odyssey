.. image:: https://travis-ci.org/amueller/odyssey.svg?branch=master
    :target: https://travis-ci.org/amueller/odyssey

Odyssey
========================

Odyssey ⛴ is built for analyzing python library usage on GitHub through Google BigQuery.

Introduction
------------

Historically there has been a huge gap between library developers and library users. It is very hard for authors (usually experts in some domains) to gather information about how the general users (usually non-experts) use their package, let alone guide development based off of that. Therefore, the design of API, set of default parameters, prioritization of development works, etc. all tend to be highly subjective. This has resulted in many frustrations, as what gets built is not what the public really wants or appreciates.

Odyssey is built to solve this gap. Odyssey leverages on all open source codes hosted on GitHub to get a better sense of how the user base interacts with our package-in-interest in day-to-day work. Backed up by Google BigQuery and parso, Odyssey is able to perform python-version-agnostic static analysis on terabytes of data.

Installation
------------

To install, first clone the repository and run setup.py file:

.. code-block::

    $ git clone https://github.com/amueller/odyssey
    $ cd odyssey
    $ python setup.py install


Using BigQuery
--------------
You need to have a google bigquery account and `create a service account key <https://cloud.google.com/docs/authentication/getting-started#creating_a_service_account>`_.
Then, set the ``GOOGLE_APPLICATION_CREDENTIALS`` environment variable to point to the json file containing the key.
When instantiating ``GithubPython`` you need to specify your google cloud project by name.

Documentation and Tutorial
--------------------------

See `here <http://odyssey.readthedocs.io/en/latest/>`_.

Creating the database
---------------------
You can create the database used for scikit-learn with the following SQL command, which looks for all Python files:

.. code-block::

    SELECT a.id id, size, content, binary, copies,
    repo_name, path, repos_c
    FROM (
    SELECT id, FIRST(repo_name) repo_name, FIRST(path) path, COUNT(UNIQUE(repo_name)) repos_c
    FROM [bigquery-public-data:github_repos.files]
    WHERE RIGHT(path,3)='.py'
    GROUP BY 1
    ) a
    JOIN [bigquery-public-data:github_repos.contents] b
    ON a.id=b.id

Licence
-------

This project is under BSD open source licence.

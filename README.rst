Odyssey
========================

.. image:: https://travis-ci.org/alan97/odyssey.svg?branch=master
    :target: https://travis-ci.org/alan97/odyssey

Odyssey ⛴ is built for analyzing python library usage on GitHub through Google BigQuery.

Introduction
------------

Historically there has been a huge gap between library developers and library users. It is very hard for authors (usually experts in some domains) to gather information about how the general users (usually non-experts) use their package, let alone guide development based off of that. Therefore, the design of API, set of default parameters, prioritization of development works, etc. all tend to be highly subjective. This has resulted in many frustrations, as what gets built is not what the public really wants or appreciates.

Odyssey is built to solve this gap. Odyssey leverages on all open source codes hosted on GitHub to get a better sense of how the user base interacts with our package-in-interest in day-to-day work. Backed up by Google BigQuery and parso, Odyssey is able to perform python-version-agnostic static analysis on terabytes of data.

Installation
------------

To install, first clone the repository and run setup.py file:

.. code-block::

    $ git clone https://github.com/alan97/odyssey.git
    $ cd odyssey
    $ python setup.py

Documentation and Tutorial
--------------------------

See `here <odyssey.readthedocs.io/>`_.

Licence
-------

This project is under BSD open source licence.

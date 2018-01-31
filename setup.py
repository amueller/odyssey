from setuptools import setup, find_packages

setup(
    name="odyssey",
    version="0.1",
    packages=find_packages(exclude=['joblib', 'docs', 'tests', '.cache']),

    author="Aishwarya Srinivasan",
    author_email="aishgrt@gmail.com",
    description="Tools for analyzing python package usage on GitHub through Google BigQuery",
    license="MIT",
    keywords="package usage analysis BigQuery GitHub",
    url="https://github.com/aishgrt1/odyssey/odyssey",
)

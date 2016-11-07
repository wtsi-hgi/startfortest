from setuptools import setup, find_packages

setup(
    name="test-with-irods",
    version="0.0.1",
    author="Colin Nolan",
    author_email="colin.nolan@sanger.ac.uk",
    packages=find_packages(exclude=["tests"]),
    url="https://github.com/wtsi-hgi/test-with-irods",
    license="LICENSE.txt",
    description="Simplifying the testing of software that uses iRODS.",
    long_description=open("README.md").read(),
    install_requires=[x for x in open("requirements.txt").read().splitlines() if "://" not in x],
    dependency_links=[x for x in open("requirements.txt").read().splitlines() if "://" in x],
    test_suite="testwithirods.tests"
)

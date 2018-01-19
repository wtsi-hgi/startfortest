from setuptools import setup, find_packages

try:
    from pypandoc import convert
    def read_markdown(file: str) -> str:
        return convert(file, "rst")
except ImportError:
    def read_markdown(file: str) -> str:
        return open(file, "r").read()

setup(
    name="useintest",
    version="4.1.0",
    author="Colin Nolan",
    author_email="colin.nolan@sanger.ac.uk",
    packages=find_packages(exclude=["tests"]),
    install_requires=[x for x in open("requirements.txt").read().splitlines() if "://" not in x],
    dependency_links=[x for x in open("requirements.txt").read().splitlines() if "://" in x],
    url="https://github.com/wtsi-hgi/useintest",
    license="MIT",
    description="I don't care how it's done, I just want to use it in my tests!",
    long_description=read_markdown("README.md"),
    test_suite="useintest.tests",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License"
    ]
)

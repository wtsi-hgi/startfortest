# FIXME: This is not cross platform...
from abc import ABCMeta

import docker

MOUNTABLE_TEMP_DIRECTORY = "/tmp"

docker_client = docker.from_env()


class UseInTestError(Exception):
    """
    Base class for all custom exceptions defined in this package.
    """


class MissingDependencyError(UseInTestError):
    """
    Raised when an optional package is not installed.
    """
    def __init__(self, package_name: str):
        super().__init__(f"Optional Python dependency `{package_name}` must be installed separately to use this "
                         f"functionality")


class UseInTestModel(metaclass=ABCMeta):
    """
    Base which all models in this package should extend.
    """



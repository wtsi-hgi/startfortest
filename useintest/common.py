# FIXME: This is not cross platform...
MOUNTABLE_TEMP_DIRECTORY = "/tmp"


class UseInTestError(Exception):
    """
    Base class for all custom exceptions defined in this package.
    """


class MissingDependencyError(UseInTestError):
    """
    Raised when an optional package is not installed.
    """
    def __init__(self, package_name: str):
        super().__init__("Optional Python dependency `{package_name}` must be installed separately to use this "
                         "functionality")

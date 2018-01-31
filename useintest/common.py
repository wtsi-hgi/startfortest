class UseInTestError(Exception):
    """
    Base class for all custom exceptions defined in this package.
    """


class MissingDependencyError(UseInTestError):
    """
    TODO
    """
    def __init__(self, package_name: str):
        super().__init__("Optional Python dependency `%s` must be installed to use this functionality"
                         % (package_name, ))

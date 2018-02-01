from useintest.common import UseInTestError


class ServiceStartError(UseInTestError):
    """
    Exception for when a service has failed to start.
    """


class TransientServiceStartError(ServiceStartError):
    """
    Exception for when a service has failed to start due to a (suspected) transient issue.
    """


class PersistentServiceStartError(ServiceStartError):
    """
    Exception for when a service has failed to start due to a (suspected) persistent issue.
    """


class UnexpectedNumberOfPortsError(UseInTestError):
    """
    Exception for when the number of ports is not as expected.
    """

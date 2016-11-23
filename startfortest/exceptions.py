class ServiceStartException(Exception):
    """
    Exception for when a service has failed to start.
    """


class TransientServiceStartException(ServiceStartException):
    """
    Exception for when a service has failed to start due to a (suspected) transient issue.
    """


class PersistentServiceStartException(ServiceStartException):
    """
    Exception for when a service has failed to start due to a (suspected) persistent issue.
    """


class UnexpectedNumberOfPortsException(Exception):
    """
    Exception for when the number of ports is not as expected.
    """

class ContainerStartException(Exception):
    """
    Exception for when a container has failed to start.
    """

class TransientContainerStartException(ContainerStartException):
    """
    Exception for when a container has failed to start due to a (suspected) transient issue.
    """

class PersistentContainerStartException(ContainerStartException):
    """
    Exception for when a container has failed to start due to a (suspected) persistent issue.
    """

class UnexpectedNumberOfPortsException(Exception):
    """
    Exception for when the number of ports is not as expected.
    """

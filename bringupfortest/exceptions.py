class ContainerStartException(Exception):
    """
    Exception to be thrown if a container has failed to start.
    """

class TransientContainerStartException(ContainerStartException):
    """
    TODO
    """

class PersistentContainerStartException(ContainerStartException):
    """
    TODO
    """

class UnexpectedNumberOfExposedPortsException(Exception):
    """
    TODO
    """

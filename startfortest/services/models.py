from bidict import bidict
from hgicommon.models import Model

from startfortest.services.exceptions import UnexpectedNumberOfPortsException


class Service(Model):
    """
    Model of a service.
    """
    def __init__(self):
        """
        Constructor.
        """
        super().__init__()
        self.host = "localhost"
        self.ports = bidict()

    @property
    def port(self) -> int:
        """
        Gets the port on the localhost. If there is more than one port exposed, an
        `UnexpectedNumberOfPortsException` will be raised.
        :return: the exposed port
        """
        if len(self.ports) != 1:
            raise UnexpectedNumberOfPortsException("%d ports are exposed (cannot use `port`)" % len(self.ports))
        return list(self.ports.values())[0]

    def get_external_port_mapping_to(self, port: int) -> int:
        """
        Gets the port on localhost to which the given port in the container maps to.
        :param port: the port inside the container
        :return: the port outside that maps to that in the container
        """
        return self.ports.inv[port]


class DockerisedService(Service):
    """
    Model of a service running in a Docker container.
    """
    def __init__(self):
        super().__init__()
        self.name = None
        self.container = None

from bidict import bidict

from bringupfortest.exceptions import UnexpectedNumberOfExposedPortsException
from hgicommon.docker.models import Container as HgiCommonContainer


class Container(HgiCommonContainer):
    """
    TODO
    """
    def __init__(self):
        super().__init__()
        self.host = "localhost"
        self.ports = bidict()

    @property
    def port(self):
        """
        TODO
        :return:
        """
        if len(self.ports) != 1:
            raise UnexpectedNumberOfExposedPortsException("%d ports are exposed" % len(self.ports))
        return list(self.ports.values())[0]

    def get_external_port_mapping_to(self, port: int) -> int:
        """
        TODO
        :param port:
        :return:
        """
        return self.ports.inv[port]



from typing import Dict

from hgicommon.docker.models import Container as HgiCommonContainer


class Container(HgiCommonContainer):
    """
    TODO
    """
    def __init__(self):
        super().__init__()
        self.host = "localhost"
        self.internal_ports_map_to = dict()     # type: Dict[int, int]

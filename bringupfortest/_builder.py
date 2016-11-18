from typing import Callable, List

from bringupfortest.controllers import DockerController


class DockerControllerBuilder:
    """
    TODO
    """
    def __init__(self, name: str, repository: str, tag: str, started_detection: Callable[[str], bool],
                 exposed_ports: List[int]):
        """
        TODO
        :param name:
        :param specification:
        """
        self.name = name
        self.repository = repository
        self.tag = tag
        self.started_detection = started_detection
        self.exposed_ports = exposed_ports

    def build(self) -> type:
        """
        TODO
        :return:
        """
        def init(controller_self: DockerController, *args, **kwargs):
            super(type(controller_self), controller_self).__init__(
                self.repository, self.tag, self.exposed_ports, *args, **kwargs)

        return type(
            self.name,
            (DockerController, ),
            {
                "__init__": init
            }
        )

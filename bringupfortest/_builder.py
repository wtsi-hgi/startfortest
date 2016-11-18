from typing import Callable, List

from bringupfortest.controllers import DockerController


class DockerControllerBuilder:
    """
    TODO
    """
    def __init__(self, name: str, repository: str, tag: str, started_detection: Callable[[str], bool],
                 ports: List[int]):
        self.name = name
        self.repository = repository
        self.tag = tag
        self.started_detection = started_detection
        self.ports = ports

    def build(self) -> type:
        """
        TODO
        :return:
        """
        def init(controller_self, *args, **kwargs):
            super(type(controller_self), controller_self).__init__(
                self.repository, self.tag, self.ports, self.started_detection, *args, **kwargs)

        return type(
            self.name,
            (DockerController, ),
            {
                "__init__": init
            }
        )

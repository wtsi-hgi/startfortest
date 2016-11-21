from bringupfortest.controllers import DockerController


class DockerControllerBuilder:
    """
    TODO
    """
    def __init__(self, name: str, *args, superclass: type=DockerController, **kwargs):
        self.name = name
        self.superclass = superclass
        self.args = args
        self.kwargs = kwargs

    def build(self) -> type:
        """
        TODO
        :return:
        """
        def init(controller_self, *args, **kwargs):
            super(type(controller_self), controller_self).__init__(
                *self.args, *args, **{**self.kwargs, **kwargs})

        return type(
            self.name,
            (self.superclass, ),
            {"__init__": init}
        )

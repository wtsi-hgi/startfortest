from abc import ABCMeta

from startfortest.controllers import DockerController


class ControllerBuilder(metaclass=ABCMeta):
    """
    Builder for controllers with particular setups (e.g. repositories and tags).
    """
    def __init__(self, name: str, *args, superclass, **kwargs):
        """
        Constructor.
        :param name: name of the type that is to be created
        :param args: any arguments that are to be automatically given to the superclass constructor
        :param superclass: the superclass of the type that is to be created
        :param kwargs: any named arguments that are to be automatically given to the superclass constructor
        """
        self.name = name
        self.superclass = superclass
        self.args = args
        self.kwargs = kwargs

    def build(self) -> type:
        """
        Builds the new controller type.
        :return: the new controller type
        """
        def init(controller_self, *args, **kwargs):
            super(type(controller_self), controller_self).__init__(
                *self.args, *args, **{**self.kwargs, **kwargs})

        return type(
            self.name,
            (self.superclass, ),
            {"__init__": init}
        )


class DockerControllerBuilder(ControllerBuilder):
    """
    Builder for Docker controllers with particular setups (e.g. repositories and tags).
    """
    def __init__(self, name: str, *args, superclass: type=DockerController, **kwargs):
        super().__init__(name, *args, superclass=superclass, **kwargs)
